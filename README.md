# Offline Judge

Offline C++ judge for the **C++ & Problem Solving Bootcamp (Level 0)**. It grades one
student `.cpp` submission against one testcase file and prints every testcase as passed
or failed plus the total score.

The judge uses only the Python standard library and a C++17 `g++` compiler. It runs on
Windows (MinGW from Code::Blocks) and on Linux/macOS where `g++` is available.

---

## Requirements

- Python 3.8 or newer.
- `g++` with C++17 support, available on `PATH`.
- On Windows, the MinGW `bin` folder from Code::Blocks must be on `PATH`.

Check both commands before grading:

```text
python --version
g++ --version
```

Use `python3` instead of `python` on Linux/macOS if that is how Python is installed.

---

## Quick start

Run the judge from the project root. It takes exactly two arguments: the student file
and the testcase file.

Windows `cmd`:

```cmd
python judge.py Subtests\demo\alice_1001.cpp Testcases\demo.txt
```

Linux/macOS:

```bash
python3 judge.py Subtests/demo/alice_1001.cpp Testcases/demo.txt
```

The last line should be:

```text
TOTAL SCORE: 30/30
```

If the project path contains spaces or `&`, quote the folder when changing into it:

```bash
cd "/path/to/offline-judge"
```

---

## What one run does

1. Parses and validates the testcase file.
2. Reads line 1 of the student file for the name, email, and student ID.
3. Extracts each `/* Problem N ... */` block as a separate program.
4. Screens the code for forbidden calls and wrong I/O style.
5. Flags the file for manual review when the header, filename, or code is unacceptable.
6. Compiles and runs each answer block, compares outputs, and prints the score.

See the [user guide](Docs/offline_judge_user_guide.md) for the full flow and verdicts.

---

## Work folders and cleanup

Each run uses `work/<student>/` to hold generated `pN.cpp` and `pN.exe` files.

- **All problems fully AC:** the student folder is deleted, and `work/` is removed if empty.
- **Any problem fails** (`CE`, `WA`, `RE`, `TLE`, `OLE`, partial score, or `MISSING`):
  the folder is kept, and the judge prints hints such as:
  ```text
  Problem 2 failed - see work/bob_1002/p2.cpp
  Artifacts kept in work/bob_1002
  ```
- **Manual review** happens before the folder is created, so nothing is kept.
- `__pycache__/` folders are removed automatically when Python exits normally.

Kept folders remain until that student is run again or `work/` is deleted manually.
`work/` and `__pycache__/` are ignored by git.

---

## Exit codes

| Code | Meaning |
|---|---|
| `0` | The file was judged; read the printed report |
| `1` | Usage problem, missing file, or invalid testcase file |
| `2` | The file needs manual review and was not auto-scored |

---

## Demo submissions

`Subtests/demo/` contains eight sample students, each designed to show a different
result. The expected outcomes and the break-it samples are described in the
[user guide](Docs/offline_judge_user_guide.md#8-demo-students-and-expected-results).

---

## Tests

Run these after changing the judge:

```bash
python3 test_extractor.py
python3 test_testcases.py
python3 test_runner.py
python3 test_safety.py
python3 test_cleanup.py
python3 test_judge.py
```

Use `python` instead of `python3` on Windows. The runner test waits for timeouts and
takes about 8 seconds. A full pass leaves no `work/` or `__pycache__/` behind.

---

## Project layout

```text
offline-judge/
├── config.py             settings (paths, compiler, flags, timeouts, scoring)
├── cleanup.py            removes work folders and __pycache__
├── extractor.py          reads a student .cpp file
├── testcases.py          reads and validates a testcase file
├── safety.py             screens code before running it
├── runner.py             compiles, runs, compares output, scores
├── judge.py              main program
├── test_*.py             self-tests
├── Docs/                 user, testcase, and developer documentation
├── Subtests/demo/       demo student submissions
├── Subtests/breakit/    submissions that test error handling
└── Testcases/            testcase files (for example demo.txt)
```

---

## Documentation

- [User guide](Docs/offline_judge_user_guide.md) - running the judge, verdicts,
  artifacts, troubleshooting.
- [Testcase format guide](Docs/testcase_format_guide.md) - how to write valid
  testcase files.
- [Developer guide](Docs/developer_guide.md) - architecture, cleanup lifecycle,
  cross-platform notes, tests, and known risks.

---

## Important limitations

- The judge handles one student file per run; there is no folder/batch mode.
- It is a safety **screen**, not a sandbox. Run untrusted submissions on a spare
  machine or restricted account.
- There is no memory limit, and the run timeout is 2 seconds per case.
- Output comparison ignores trailing spaces on a line and trailing blank lines only.
- `cin`/`cout`-only is a warning, not a hard rule.
- Scores are printed to the console; there is no CSV output yet.
