# Developer Guide

This guide explains how the offline judge is built, where to change behavior, how the
cleanup rules work, and what to test after a change.

---

## 1. Architecture

The judge is a single-pass pipeline. Each module has one job:

| File | Responsibility |
|---|---|
| `config.py` | All settings: paths, compiler, flags, timeouts, output limit, case counts, points |
| `cleanup.py` | Removes build folders and `__pycache__`; registers cache cleanup at exit |
| `extractor.py` | Reads line 1 and splits a student file into problem blocks |
| `testcases.py` | Parses and validates a testcase file |
| `safety.py` | Screens answer code for forbidden calls/headers and old-style I/O |
| `runner.py` | Compiles one block, runs its cases, compares output, computes the score |
| `judge.py` | Main program: checks arguments, manual review, builds the report, keeps/deletes work |
| `Dev_Tests/` | Self-tests, one file per module plus judge integration and cleanup |

Folder layout:

```text
offline-judge/
├── config.py, cleanup.py, extractor.py, testcases.py, safety.py, runner.py, judge.py
├── Dev_Tests/              self-tests, run with python3 -m from the project root
├── Docs/
├── Subtests/demo/          normal demo submissions
├── Subtests/breakit/       error-handling samples
└── Testcases/              testcase files
```

`RESULTS_DIR` in `config.py` and the `results/` line in `.gitignore` are leftovers from
the old CSV-output batch. No current code writes there.

---

## 2. Data flow

```text
command line
   │
   ├─ testcases.parse_testcases(path) ──> {problem: [case, ...]}
   │
   ├─ extractor.extract_submission(path) ──> header, problems, warnings
   │
   ├─ safety.find_forbidden / find_style_warnings
   │
   ├─ judge.check_manual_review
   │
   ├─ work/<stem>/pN.cpp
   │
   ├─ runner.compile_source ──> pN.exe or CE
   │
   ├─ runner.run_one for each case ──> AC / WA / TLE / OLE / RE
   │
   └─ runner.judge_problem ──> status, verdicts, passed, score
```

### Data shapes

`parse_testcases` returns:

```python
{
    1: [
        {
            "number": 1,
            "edge": False,
            "points": 1,
            "input": "10 20\n",
            "output": "30\n",
        },
        ...
    ]
}
```

`extract_submission` returns:

```python
{
    "header": {"name": "...", "email": "...", "student_id": "..."},
    "header_error": "",
    "problems": {1: "full program text", 2: "..."},
    "warnings": ["..."],
}
```

`judge_problem` returns:

```python
{
    "status": "AC" | "PARTIAL" | "FAIL" | "CE",
    "passed": 4,
    "total": 8,
    "score": 6,
    "max_score": 10,
    "verdicts": ["AC", "WA", ...],
    "note": "compiler output when status is CE",
}
```

---

## 3. Config reference

| Setting | Default | Notes |
|---|---|---|
| `SUBMISSIONS_DIR` | `Subtests` | Demo and break-it submissions |
| `TESTS_DIR` | `Testcases` | Testcase files |
| `WORK_DIR` | `work` | Generated sources and binaries |
| `RESULTS_DIR` | `results` | Legacy, unused |
| `COMPILER` | `g++` | Must be on `PATH` |
| `COMPILER_FLAGS` | `-std=c++17 -O2` | Used for every block |
| `COMPILE_TIMEOUT_SEC` | `30` | Per block |
| `RUN_TIMEOUT_SEC` | `2` | Per testcase |
| `MAX_OUTPUT_BYTES` | `1000000` | Program is killed while printing past this |
| `BASE_CASE_COUNT` | `6` | Cases 1 to 6 |
| `EDGE_CASE_COUNT` | `2` | Cases 7 and 8 |
| `BASE_POINTS` | `1` | Per base case |
| `EDGE_POINTS` | `2` | Per edge case |
| `CHECK_FILENAME_ID` | `True` | Compare filename ID with header ID |

Changing case counts or points also requires updating `testcases` expectations in
`Dev_Tests/test_testcases.py` and the documented examples.

---

## 4. Cross-platform behavior

The judge targets Windows and Linux/macOS. It works on both because:

- It uses only portable Python standard-library modules: `os`, `subprocess`, `shutil`,
  `re`, `threading`, `atexit`, `tempfile`.
- Paths are built with `os.path.join`, never with hardcoded separators.
- Compilation is a direct `subprocess.run([...])` with no shell, so Windows `cmd`
  syntax is not involved.
- `g++` is available on both systems (MinGW on Windows, native compiler on Linux).
- The `.exe` suffix is only a filename convention on Linux; `g++` still marks the
  output executable, so `Popen([exe])` works.
- Text is read and written explicitly as UTF-8; Windows line endings are normalized.

Linux-specific risks:

- If `g++` is missing, `subprocess.run` raises `FileNotFoundError`, which is not caught.
- A build folder on a `noexec` filesystem cannot run the generated binary.
- `proc.kill()` stops only the direct child; grandchildren survive.
- Removing `__pycache__` while another judge process is running is harmless on Linux
  because the files are already open or unlinked, but it is best to avoid concurrent
  runs.

---

## 5. Cleanup lifecycle

`cleanup.py` owns temporary-file behavior.

### `__pycache__`

`remove_pycache()` walks `config.BASE_DIR`, deletes every `__pycache__` folder, and
skips `.git`. It is registered with `atexit`, so every entry point that imports
`cleanup` removes caches when Python exits normally. It does not run after `kill -9`,
SIGKILL, or a power loss.

### `work/`

`judge.py` uses `work/<student_stem>/` for `pN.cpp` and `pN.exe`.

| Run outcome | Cleanup |
|---|---|
| All problems fully AC | `remove_build_dir(build_dir)`, then remove `work/` if empty |
| Any problem not fully AC | Keep `work/<stem>/` and print hints |
| Missing problem | Keep the folder; print `no answer block was submitted` |
| Manual review | No folder was created |
| Unexpected exception or Ctrl-C | Print the kept path, then re-raise |

At startup, `judge.py` removes only the current student's folder. It never wipes all of
`work/`, because other students' failed runs are intentionally kept. Failed folders
accumulate until the student is rerun or the reviewer deletes `work/`.

`Dev_Tests/test_runner.py` removes its own `work/_runner_test/` and then removes
`work/` if empty.

---

## 6. Runner behavior

`compile_source` writes `<name>.cpp` and compiles to `<name>.exe`.

`run_one`:

- sends the case input through stdin,
- reads stdout in a background thread,
- kills the process when output passes `MAX_OUTPUT_BYTES`,
- kills the process after `RUN_TIMEOUT_SEC`,
- discards stderr,
- returns `TLE`, `OLE`, `RE`, or `OK`.

`judge_problem` maps `OK` to `AC` or `WA` via `normalize`, which:

- converts `\r\n` to `\n`,
- strips trailing spaces from every line,
- drops trailing blank lines.

A non-zero exit code is `RE` even when the printed answer is correct.

---

## 7. Safety model

`safety.py` is a **screen**, not a sandbox. It removes string/character literals and
`//` comments, then searches for:

- process, file-deletion, network, and library-loading calls,
- system headers such as `windows.h`, `unistd.h`, `fstream`, and `filesystem`,
- inline assembly.

A match sends the file to manual review before anything is compiled. This reduces
accidental damage but does not make untrusted code safe. Run submissions on a spare
machine or a restricted account.

Old-style I/O (`scanf`, `printf`, `puts`, `gets`, `getchar`) produces a warning only.

---

## 8. Testing

Run every test from the project root after changing behavior:

```bash
python3 -m Dev_Tests.test_extractor    # 26 checks
python3 -m Dev_Tests.test_testcases    # 12 checks
python3 -m Dev_Tests.test_runner       # 8 checks, about 8 seconds of timeouts
python3 -m Dev_Tests.test_safety       # 9 checks
python3 -m Dev_Tests.test_cleanup      # 6 checks
python3 -m Dev_Tests.test_judge        # 11 checks
```

Use `python -m ...` on Windows. Running the modules with `-m` keeps the project root on
`sys.path`, so the tests can import `config`, `cleanup`, `extractor`, and the other
modules without path changes.

`Dev_Tests/test_judge.py` runs the real CLI through `subprocess` and checks work
retention:

- `alice` is fully AC, so the folder is deleted.
- `dave` has a runtime error and a missing block, so the folder and hints are kept.
- `frank` needs manual review, so no folder is created.

Manual smoke test for the full report:

```bash
python3 judge.py Subtests/demo/alice_1001.cpp Testcases/demo.txt
```

A full pass leaves no `work/` or `__pycache__/` behind.

---

## 9. How to extend

### Add a new check or verdict

1. Change the module that produces it (`runner.py` for run results, `safety.py` for
   screening).
2. Add a case to the matching `Dev_Tests/test_*.py`.
3. Update the verdict table in the user guide and the README if it is user-visible.

### Add a new testcase rule

1. Change `testcases.py`.
2. Add a `check(...)` to `Dev_Tests/test_testcases.py`.
3. Update `Docs/testcase_format_guide.md`.

### Add batch/folder mode

Keep one build directory per student so cleanup and retention stay understandable. Do
not wipe all of `work/` at startup; that would delete kept failures from other students.

### Add CSV output

`RESULTS_DIR` already exists. Write one row per student with
`student_id,name,assignment,auto_score`, and add a test. Keep the console report.

---

## 10. Known limitations and risks

- No sandbox and no memory limit; only time and output size are limited.
- `proc.kill()` does not kill descendant processes.
- The run timeout is 2 seconds, while the assignment template says 1 second.
- No folder/batch mode and no CSV output.
- No roster check; name and ID are not validated against registration data.
- A data line that exactly equals a section label is parsed as a label.
- Duplicate problem blocks keep the first one.
- Failed `work/` folders remain until rerun or manual deletion.
- `__pycache__` cleanup does not run after SIGKILL or power loss.
- The demo relies on signed `int` overflow, which is undefined behavior in C++.

Possible future work: batch mode, CSV output, memory limits, process-group killing, a
stronger sandbox, roster validation, and an explicit cleanup command.
