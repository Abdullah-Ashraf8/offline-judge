# Offline Judge: Project Status Document

Offline C++ judge for the **C++ & Problem Solving Bootcamp (Level 0)**.
Project folder: `E:\judge`. Status as of **2 Nov 2026**.

---

## 1. Project at a glance

| Item | Detail |
|---|---|
| Goal | Judge one student's `.cpp` submission against one testcase file, then print every testcase as passed or failed plus the total score |
| Programme | C++ & Problem Solving Bootcamp, Level 0 (programming fundamentals; no OOP, pointers, or memory management this semester) |
| Why offline | Google Classroom has no code autograding, so grading runs on a Windows machine with hidden edge-case tests |
| Environment | Windows, cmd terminal, VS Code, Python 3 (standard library only), g++ (MinGW from Code::Blocks) with `-std=c++17` |
| Deadline | Ready before Week 1 (11/8). Week 0 starts 11/1 |
| Interface | `python judge.py <assignment_file.cpp> <testcase_file.txt>` |
| Output | Plain text in the console, no CSV (team leader decision) |

---

## 2. Background from the course plan

- Six assignments, each worth 100 to 150 points (10 to 15 problems at 10 points each under the spec).
- Students write solutions in Code::Blocks on Windows, using `cin` and `cout` only.
- Students submit one `.cpp` file per assignment, with every answer written inside a `/* ... */` comment.
- About 116 students are registered (from the plan).
- Things the judge does **not** do (handled by the reviewers): bonus points, the 5% cleanliness/originality mark, strike deductions, and AI-policy checks such as the bonus-problem trick and recorded explanations. These are tracked in `Leaderboard.xlsx` per the spec.

---

## 3. The format spec (`judge_formats.md`) in brief

### 3.1 Student file
- File name: `<Name>_<StudentID>.cpp`, for example `Hassan_PS123.cpp`.
- **Line 1** must be the identification comment:
  `// Name:[your full name]  Email:[your email]  Student ID:[your ID]`
- Each answer is a block starting with `/* Problem N` on its own line and ending with `*/`.
- `//` comments inside a block are allowed. `*/` inside code ends the block early and is not allowed.
- A missing block scores 0 for that problem. For duplicate blocks the first one is used.
- A missing or malformed header means the file is flagged for manual review and is not auto-scored.

### 3.2 Testcase file (one per assignment)
```
Problem 1
Case 1:
Input:
<input lines>
Output:
<expected output lines>
...
Case 7 (Edge):
Input:
...
Output:
...
```
- 8 cases per problem. Cases 1 to 6 are base cases (1 point each). Cases 7 and 8 are edge cases, labeled `Case N (Edge):` (2 points each). Total 10 points per problem.
- Output comparison ignores trailing spaces on each line and blank lines at the end. Everything else must match exactly.

### 3.3 Scores output (spec)
One CSV per assignment with columns `student_id,name,assignment,auto_score`, produced with pandas. **The team leader has decided this is not needed for now** (see section 4).

---

## 4. Decisions log

| # | Decision | Source |
|---|---|---|
| 1 | The program takes only two paths: the assignment file and the testcase file. No assignment number and no folder conventions | Team leader |
| 2 | Plain console output: passed or failed per testcase plus the total score. No CSV for now | Team leader |
| 3 | A file needing manual review makes the program raise an error that names the file and what to fix | Team leader |
| 4 | Every answer block is a complete program with its own `#include` and `main` | Team leader |
| 5 | Header brackets are optional. Unchanged template text (such as `your full name`) counts as unfilled | Built in (spec silent) |
| 6 | The ID in the filename must match the header ID. Switch: `CHECK_FILENAME_ID` in `config.py` | Built in (not yet confirmed by the team) |
| 7 | Duplicate problem blocks keep the first one and give a warning | Spec ("to be confirmed") |
| 8 | Compile flags `-std=c++17 -O2`, 2 second limit per testcase | Built in (the template says 1 second) |
| 9 | Exit codes: 0 judged, 1 usage or file problem, 2 manual review | Built in |
| 10 | Answer blocks may also contain a title line, a dashed separator, or `*` at the start of every line. The extractor tolerates these | Built in |

---

## 5. Current files and what they do

```
E:\judge\
├── config.py             settings
├── extractor.py          reads a student file
├── testcases.py          reads the testcase file
├── runner.py             compiles and runs code, compares output
├── judge.py              main program (the one you run)
├── test_extractor.py     26 automated checks
├── test_testcases.py     12 automated checks
├── test_runner.py        7 automated checks
├── submissions\demo\     8 demo student files
├── tests\demo.txt        demo testcase file (3 problems, 8 cases each)
├── work\                 temporary build folder (auto-created)
├── results\              left over from Batch 2, no longer used
└── __pycache__\          Python cache (auto-created)
```

| File | What it does |
|---|---|
| `config.py` | Holds all settings: folder paths, compiler `g++` with flags `-std=c++17 -O2`, compile timeout 30 s, run timeout 2 s, output limit 1,000,000 characters, case counts (6 base, 2 edge), points (1 per base case, 2 per edge case), and `CHECK_FILENAME_ID = True` |
| `extractor.py` | `extract_submission(path)` returns the header (`name`, `email`, `student_id`), a `header_error` text (empty when the header is fine), the code of each problem, and a list of warnings. `filename_id(name)` returns the ID part of `Name_ID.cpp`. It can also be run by itself: `python extractor.py file.cpp` |
| `testcases.py` | `parse_testcases(path)` reads the testcase file into `{problem: [cases]}` and raises `ValueError` listing every format error with line numbers |
| `runner.py` | `judge_problem(code, cases, build_dir, name)` compiles one answer, runs it on every case, and returns the verdicts and score |
| `judge.py` | The main program. Defines `ManualReviewError`, checks the file, judges every problem, and prints the report |
| `test_*.py` | Self-tests. Run them after any change |
| `tests\demo.txt` | Demo testcases in the spec format |
| `submissions\demo\*.cpp` | Eight fake students, each designed to fail in a specific way (section 7) |

---

## 6. How the program works, step by step

Example command:
```
python judge.py submissions\demo\bob_1002.cpp tests\demo.txt
```

### Step 1: Check the arguments
Exactly two arguments are needed. Otherwise it prints the `usage:` and `example:` lines and exits with code 1. If either file is missing, it prints `assignment file not found: ...` or `testcase file not found: ...` and exits with code 1.

### Step 2: Read the testcase file (`testcases.py`)
Reads `tests\demo.txt` line by line:
- `Problem 2` starts a problem.
- `Case 7 (Edge):` starts a case and marks it as an edge case.
- `Input:` and `Output:` start the data blocks.

It validates that each problem has cases 1 to 8 in order, with cases 7 and 8 labeled `(Edge)`, every case has one `Input:` and one `Output:`, and no output is empty. If anything is wrong it prints `testcase file has errors:` and the line-numbered problems, then exits with code 1.

Result for the example snippet `Case 7 (Edge):` / `-5 5` / `0`:
```python
{"number": 7, "edge": True, "points": 2, "input": "-5 5\n", "output": "0\n"}
```

### Step 3: Read the student file (`extractor.py`)
- **Line 1** is matched against the header pattern. Example:
  `// Name:Alice Hassan  Email:alice@example.com  Student ID:1001`
  becomes `{'name': 'Alice Hassan', 'email': 'alice@example.com', 'student_id': '1001'}`. Brackets are removed if present, and template text left unchanged counts as empty.
- Every `/* ... */` block whose first line starts with `Problem N` becomes the code for problem N. A title (`Problem 1 - Double It`), a dashed line, and a `*` at the start of every line are tolerated and removed.
- **Warnings:** `duplicate problem N (kept first)`, `problem N block is empty`, and `stray text outside comment blocks` (what a nested `*/` leaves behind).

### Step 4: Manual-review check (`judge.py`)
The program raises `ManualReviewError` when:
- the header is missing or malformed (`header_error` is not empty), or
- the filename has no `_ID` part, or the filename ID differs from the header ID (only while `CHECK_FILENAME_ID` is `True`).

The error is printed to stderr and the exit code is 2. Example:
```
ERROR: this file needs manual review: heidi_1008.cpp - first line is not the identification comment. To fix: line 1 must be: // Name:[your full name]  Email:[your email]  Student ID:[your ID]
```

### Step 5: Print the header and warnings
```
File   : bob_1002.cpp
Student: Bob Samir (1002)
```
Warnings, if any, follow as `WARNING: ...` lines.

### Step 6: Prepare a clean build folder
`work\<file name without .cpp>` is deleted and recreated. For Bob it is `work\bob_1002`.

### Step 7: Judge each problem (`runner.py`)
For each problem number in the testcase file, in order:

1. **Missing block:** prints `MISSING - no answer block for this problem`, scores 0, and moves on.
2. **Compile:** writes the code to `work\bob_1002\p2.cpp` and runs `g++ -std=c++17 -O2 p2.cpp -o p2.exe` (30 second limit). On failure every case gets verdict `CE`, and the first 8 compiler lines are printed.
3. **Run each case:** the case input is sent to the program, with a 2 second limit.

   | Verdict | Meaning |
   |---|---|
   | `TLE` | took longer than 2 seconds |
   | `OLE` | printed more than 1,000,000 characters |
   | `RE` | exit code was not 0 (even if the printed answer was right) |
   | `AC` | output matches the expected output after normalizing |
   | `WA` | output differs |

   Normalizing means trailing spaces on each line are ignored, trailing blank lines are ignored, and Windows line endings are treated as normal.
4. **Score:** the problem score is the sum of the points of the `AC` cases, out of a maximum of 10.

Example: Bob's Problem 2 uses `a - b`. Only case 5 (`0 0` gives `0`) passes, so the score is 1 out of 10.

### Step 8: Print the report and total
```
Problem 2
  Case 1:        FAILED   +0 of 1  [WA]
  Case 2:        FAILED   +0 of 1  [WA]
  Case 3:        FAILED   +0 of 1  [WA]
  Case 4:        FAILED   +0 of 1  [WA]
  Case 5:        PASSED   +1
  Case 6:        FAILED   +0 of 1  [WA]
  Case 7 (Edge): FAILED   +0 of 2  [WA]
  Case 8 (Edge): FAILED   +0 of 2  [WA]
  Problem 2 score: 1/10
```
Bob's last line is `TOTAL SCORE: 11/30` (Problem 1 gives 10, Problem 2 gives 1, and Problem 3 is an infinite loop that times out, giving 0).

---

## 7. Demo students and expected results

Run each with `python judge.py submissions\demo\<file> tests\demo.txt`.

| File | Scenario | Expected result |
|---|---|---|
| `alice_1001.cpp` | Everything correct, header without brackets | `TOTAL SCORE: 30/30` |
| `bob_1002.cpp` | `a - b` bug in Problem 2, infinite loop in Problem 3 | `11/30` (10 + 1 + 0) |
| `carol_1003.cpp` | Compile error in Problem 1, `int` overflow in Problem 2, `best = 0` in Problem 3 | `14/30` (0 + 8 + 6) |
| `dave_1004.cpp` | Star-prefixed answers, Problem 2 returns exit code 1, Problem 3 missing | `10/30` (10 + 0 + MISSING) |
| `eve_1005.cpp` | A nested `/* */` breaks Problem 2 | `20/30` plus `WARNING: stray text outside comment blocks` |
| `frank_1006.cpp` | Header ID `9999` does not match filename ID `1006` | Manual-review error, exit code 2 |
| `grace_1007.cpp` | Header with brackets | `30/30` |
| `heidi_1008.cpp` | Line 1 is not the identification comment | Manual-review error, exit code 2 |

---

## 8. How to run and test

From `E:\judge`:
```
python test_extractor.py     (expect 26 / 26 checks passed)
python test_testcases.py     (expect 12 / 12 checks passed)
python test_runner.py        (expect 7 / 7 checks passed, about 15 seconds)
python judge.py submissions\demo\alice_1001.cpp tests\demo.txt
```
Check the exit code with `echo %errorlevel%`.

Requirement: `g++ --version` must work in the same terminal (add the MinGW `bin` folder to PATH if it does not).

---

## 9. Progress and verification history

| Stage | Steps | What was built | Status |
|---|---|---|---|
| Batch 1 | 1 to 11 | Environment, folders, `config.py`, `extractor.py`, demo files, extractor tests | Verified (all checks passed) |
| Batch 2 | 12 to 19 | Test data, `runner.py`, first `judge.py`, CSV output | Verified (scores matched) |
| Spec alignment | 20 to 33 | New header, `testcases.py`, new scoring, `ManualReview` rules, new demo set | Verified: "completely good, no errors" |
| Team leader decisions | 34 to 38 | Plain-output `judge.py` with two path arguments, `ManualReviewError`, `CHECK_FILENAME_ID` | Delivered, not yet confirmed by running |

---

## 10. Known limitations and risks

- **One file per run:** the judge handles a single student file. Judging a whole folder means running it once per file.
- **No sandbox yet:** student code runs with your user's permissions and could read or delete files. Run it only on a spare machine or a restricted account until Batch 3.
- **No memory limit:** the template says 256 MB, the judge only enforces the time limit.
- **Time limit:** the judge uses 2 seconds, while the template says 1 second.
- **Signed overflow:** the demo relies on `int` overflow wrapping (it does in practice, and the Batch 2 run confirmed it), which is technically undefined behavior in C++.
- **Testcase labels:** a data line that exactly equals `Problem N`, `Case N:`, `Input:`, or `Output:` would be read as a label.
- **I/O style:** `cin`/`cout` only is not enforced. A solution using `scanf` still compiles and runs.
- **No roster check:** the spec says name and ID must match registration data, and the judge has no registration list.
- **pandas:** installed during Step 20 but no longer used.

---

## 11. Open decisions for the team (documents that disagree)

- **Points:** the assignment template has varying points per problem (5 to 20) and bonus problems 13 to 15 worth +10, +10, +15. The spec says a flat 10 per problem and bonus points are added by reviewers. Decide whether problems 13 to 15 are judged at 10 points each or reviewed separately.
- **Template header:** the template's multi-line header with `Assignment #` must be replaced by the one-line header from the spec.
- **Template checklist:** the compile-check item (`g++ -std=c++17 your_file.cpp`) fails when every answer is inside a comment. Remove it or reword it as "paste each answer into its own file and compile it".
- **Filename example:** the template says `Hassan_Ahmed_PS001.cpp` and the spec says `Hassan_PS123.cpp`. Both work, because the ID is the text after the last underscore.
- **Filename check:** confirm whether `CHECK_FILENAME_ID` should stay on.
- **Compiler setting:** students must set Code::Blocks to C++17 so their environment matches the judge.

---

## 12. What is next

### Immediate
1. Run Steps 36 to 38 (the plain-output `judge.py`) and confirm the output matches.
2. Answer the open decisions in section 11.

### Batch 3 (on hold until you say "start Batch 3"; proposed contents)
1. **Break-it test files:** wrong filename, `scanf`, missing header, nested `*/`, huge output, and duplicate blocks, to test the judge's error handling.
2. **Real Week 1 setup:** folders such as `submissions\week1\` and `tests\week1.txt`, a process for writing the real testcases (each expected output verified with a trusted brute-force solution), and a repeatable way to run the judge on every submission.
3. **Safety hardening:** run on a spare machine or restricted account, kill runaway processes, cut off output while the program runs, add a memory limit, and refuse suspicious code (for example `system(` or file deletion).
4. **Optional roster check:** compare name and ID with registration data.

### Later, if the team wants it
- A folder mode that judges every file in a directory.
- The spec's CSV output (`student_id,name,assignment,auto_score`).
- Updates to the student-facing assignment template (section 11).
