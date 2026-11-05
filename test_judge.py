# test_judge.py - checks work-folder retention in judge.py
import os
import subprocess
import sys

import cleanup
import config

DEMO = os.path.join(config.SUBMISSIONS_DIR, "demo")
TESTS = os.path.join(config.TESTS_DIR, "demo.txt")
results = []


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    results.append(bool(condition))


def run(name):
    return subprocess.run(
        [sys.executable, "judge.py", os.path.join(DEMO, name), TESTS],
        cwd=config.BASE_DIR,
        capture_output=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )


def build_dir(stem):
    return os.path.join(config.WORK_DIR, stem)


for stem in ("alice_1001", "dave_1004", "frank_1006"):
    cleanup.remove_build_dir(build_dir(stem))
cleanup.remove_empty_work_dir()

try:
    alice = run("alice_1001.cpp")
    check("alice: judged with 30/30",
          alice.returncode == 0 and "TOTAL SCORE: 30/30" in alice.stdout)
    check("alice: work folder removed", not os.path.exists(build_dir("alice_1001")))

    dave = run("dave_1004.cpp")
    dave_dir = build_dir("dave_1004")
    check("dave: judged with 10/30",
          dave.returncode == 0 and "TOTAL SCORE: 10/30" in dave.stdout)
    check("dave: work folder kept", os.path.isdir(dave_dir))
    check("dave: source artifact kept", os.path.isfile(os.path.join(dave_dir, "p2.cpp")))
    check("dave: failed problem hint",
          "Problem 2 failed - see %s" % os.path.join("work", "dave_1004", "p2.cpp")
          in dave.stdout)
    check("dave: missing problem hint",
          "Problem 3 failed - no answer block was submitted" in dave.stdout)
    check("dave: kept summary",
          "Artifacts kept in %s" % os.path.join("work", "dave_1004") in dave.stdout)

    frank = run("frank_1006.cpp")
    check("frank: manual review exit code 2", frank.returncode == 2)
    check("frank: manual review message", "needs manual review" in frank.stderr)
    check("frank: no work folder", not os.path.exists(build_dir("frank_1006")))
finally:
    cleanup.remove_build_dir(build_dir("dave_1004"))
    cleanup.remove_empty_work_dir()

print()
print("%d / %d checks passed" % (sum(results), len(results)))
if not all(results):
    raise SystemExit(1)
