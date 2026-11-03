# runner.py - compile one answer block and run it against a list of test cases
import os
import subprocess
import threading

import config


def compile_source(code, build_dir, name):
    """Compile code into build_dir. Returns (exe_path, error_text)."""
    os.makedirs(build_dir, exist_ok=True)
    src = os.path.join(build_dir, name + ".cpp")
    exe = os.path.join(build_dir, name + ".exe")
    with open(src, "w", encoding="utf-8", newline="\n") as f:
        f.write(code)
    cmd = [config.COMPILER] + config.COMPILER_FLAGS + [src, "-o", exe]
    try:
        r = subprocess.run(
            cmd,
            capture_output=True,
            encoding="utf-8",
            errors="replace",
            timeout=config.COMPILE_TIMEOUT_SEC,
        )
    except subprocess.TimeoutExpired:
        return None, "compile timeout"
    if r.returncode != 0:
        return None, r.stderr
    return exe, ""


def normalize(text):
    """Ignore trailing spaces on each line and blank lines at the end."""
    lines = [line.rstrip() for line in text.replace("\r\n", "\n").split("\n")]
    while lines and lines[-1] == "":
        lines.pop()
    return lines


def run_one(exe, input_text, cwd):
    """Returns (verdict, output). Verdict is OK, TLE, RE or OLE.
    Output is read while the program runs, so a program that prints forever
    is killed as soon as it passes config.MAX_OUTPUT_BYTES."""
    proc = subprocess.Popen(
        [exe],
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        cwd=cwd,
    )
    chunks = []
    state = {"bytes": 0, "too_big": False}

    def reader():
        fd = proc.stdout.fileno()
        while True:
            try:
                data = os.read(fd, 4096)
            except OSError:
                break
            if not data:
                break
            state["bytes"] += len(data)
            if state["bytes"] > config.MAX_OUTPUT_BYTES:
                state["too_big"] = True
                proc.kill()
                break
            chunks.append(data)

    t = threading.Thread(target=reader, daemon=True)
    t.start()
    try:
        proc.stdin.write(input_text.encode("utf-8"))
        proc.stdin.close()
    except OSError:
        pass  # the program exited without reading its input

    try:
        proc.wait(timeout=config.RUN_TIMEOUT_SEC)
    except subprocess.TimeoutExpired:
        proc.kill()
        proc.wait()
        t.join(5)
        return "TLE", ""

    t.join(5)
    output = b"".join(chunks).decode("utf-8", errors="replace")
    if state["too_big"]:
        return "OLE", ""
    if proc.returncode != 0:
        return "RE", output
    return "OK", output


def judge_problem(code, cases, build_dir, name):
    """Compile and test one problem. cases come from testcases.py."""
    result = {
        "status": "",
        "passed": 0,
        "total": len(cases),
        "score": 0,
        "max_score": sum(c["points"] for c in cases),
        "verdicts": [],
        "note": "",
    }

    exe, error = compile_source(code, build_dir, name)
    if exe is None:
        result["status"] = "CE"
        result["note"] = error
        result["verdicts"] = ["CE"] * len(cases)
        return result

    for case in cases:
        verdict, output = run_one(exe, case["input"], build_dir)
        if verdict == "OK":
            verdict = "AC" if normalize(output) == normalize(case["output"]) else "WA"
        result["verdicts"].append(verdict)
        if verdict == "AC":
            result["passed"] += 1
            result["score"] += case["points"]

    if result["passed"] == result["total"]:
        result["status"] = "AC"
    elif result["passed"] > 0:
        result["status"] = "PARTIAL"
    else:
        result["status"] = "FAIL"
    return result