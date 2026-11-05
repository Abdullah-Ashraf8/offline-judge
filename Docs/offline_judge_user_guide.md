# Offline Judge: User Guide

This guide explains how to run the offline C++ judge, what it expects from a student
file, how it scores a submission, and where to look when something fails.

The judge grades **one student file against one testcase file** at a time.

---

## 1. What you need

- **Python 3.8 or newer.** The judge uses only the standard library.
- **A C++17 compiler.** The judge runs `g++` from `PATH` with `-std=c++17 -O2`.

### Windows

1. Install Code::Blocks with the MinGW compiler.
2. Add the MinGW `bin` folder to your `PATH`.
3. Open `cmd` and check:

```cmd
python --version
g++ --version
```

### Linux / macOS

Install `g++` if it is missing, then check both commands:

```bash
python3 --version
g++ --version
```

On Ubuntu/Debian:

```bash
sudo apt install g++
```

On macOS, install the command-line developer tools if needed:

```bash
xcode-select --install
```

---

## 2. Running one submission

Run the judge from the project root. It needs exactly two paths:

```text
python judge.py <student_file.cpp> <testcase_file.txt>
```

Windows `cmd` example:

```cmd
python judge.py Subtests\demo\alice_1001.cpp Testcases\demo.txt
```

Linux/macOS example:

```bash
python3 judge.py Subtests/demo/alice_1001.cpp Testcases/demo.txt
```

If the path contains spaces or `&`, quote the whole path:

```bash
python3 judge.py "Subtests/demo/alice_1001.cpp" "Testcases/demo.txt"
```

Use absolute paths if you prefer; both relative and absolute paths work.

Exit codes:

| Code | Meaning |
|---|---|
| `0` | The file was judged. Read the printed report. |
| `1` | Wrong usage, missing file, or invalid testcase file. |
| `2` | The file needs manual review and was not auto-scored. |

---

## 3. Submission format

### File name and header

The file must be named `<Name>_<StudentID>.cpp`, for example `Hassan_PS123.cpp`.

Line 1 must be:

```text
// Name:[your full name]  Email:[your email]  Student ID:[your ID]
```

Brackets are optional. Unchanged template text such as `your full name` counts as
unfilled. The ID in the file name must match the header ID while
`CHECK_FILENAME_ID` is enabled in `config.py`.

### Answer blocks

Each answer is a complete program inside a block comment:

```cpp
/*
 * Problem 1 - Double It
 * ----------------------
 * #include <iostream>
 * using namespace std;
 *
 * int main() {
 *     long long n;
 *     cin >> n;
 *     cout << n * 2 << endl;
 *     return 0;
 * }
 */
```

Rules:

- Start the block with `Problem N` on its own line. `Problem N - title` is also accepted.
- A dashed separator line is optional.
- If every line starts with `*`, the judge removes that prefix.
- Each block must be a complete program with its own `#include` and `main`.
- A missing block scores 0 for that problem.
- For duplicate blocks, the first one is used and a warning is printed.
- `*/` inside the answer ends the block early. The rest becomes stray text and is
  reported as a warning.

---

## 4. Step-by-step flow

### Step 1: Check the arguments

The judge requires exactly two arguments. Missing arguments or a missing file exits
with code `1`.

### Step 2: Read the testcases

The testcase file is parsed and validated. By default each problem needs exactly eight
cases:

- Cases 1 to 6 are base cases, worth 1 point each.
- Cases 7 and 8 are edge cases, written `Case N (Edge):`, worth 2 points each.
- Every case must have one `Input:` and one `Output:`, and the output cannot be empty.

Validation errors are printed with line numbers and the run exits with code `1`.
The counts and points come from `config.py`.

See the [testcase format guide](testcase_format_guide.md) for the full format.

### Step 3: Read the student file

The judge reads line 1 for the header and extracts every `/* ... */` block whose first
line starts with `Problem N`.

Warnings do not stop grading:

- `duplicate problem N (kept first)`
- `problem N block is empty`
- `stray text outside comment blocks`

### Step 4: Safety screen and manual review

Before running anything, the judge checks the answer code with `safety.py`. The file is
sent to manual review when:

- The first line is not the identification comment.
- A header field is empty or still contains template text.
- The file name has no `_ID` part, or the file name ID differs from the header ID.
- An answer uses a forbidden call or header, such as `system`, `fork`, `exec*`,
  `remove`, `socket`, `windows.h`, `unistd.h`, `fstream`, or `filesystem`.
- An answer uses inline assembly (`asm` / `__asm__`).

For these problems the judge prints `ERROR: this file needs manual review: ...` to
stderr and exits with code `2`. Nothing is compiled or kept in `work/`.

The judge also prints style warnings when code uses `scanf`, `printf`, `puts`, `gets`,
or `getchar`, because the course asks for `cin` and `cout`. These warnings do not
remove points.

### Step 5: Prepare the build folder

The judge creates `work/<student_file_stem>/`. Any older folder for the same student is
replaced before the new run starts.

### Step 6: Compile and test each problem

For each problem in the testcase file, in order:

1. If the answer block is missing, print `MISSING`, score 0, and continue.
2. Write the answer to `pN.cpp`.
3. Compile with `g++ -std=c++17 -O2`, with a 30-second limit.
4. Run every case with a 2-second limit and a 1,000,000-byte output limit.
5. Compare output after normalizing.

Normalization ignores trailing spaces on each line, trailing blank lines, and Windows
line endings. Everything else must match exactly.

### Step 7: Print the report

The report lists the student, warnings, every case verdict, each problem score, and the
total score.

---

## 5. Verdicts

| Verdict | Meaning |
|---|---|
| `AC` | Accepted: output matches the expected output after normalization. |
| `WA` | Wrong Answer: the program finished but printed the wrong output. |
| `TLE` | Time Limit Exceeded: the case ran longer than 2 seconds. |
| `OLE` | Output Limit Exceeded: the program printed more than 1,000,000 bytes. |
| `RE` | Runtime Error: the program returned a non-zero exit code or crashed. |
| `CE` | Compile Error: the block could not be compiled. All cases for that problem fail. |
| `MISSING` | The student did not include an answer block for that problem. |

A problem is fully AC only when every one of its cases is AC.

---

## 6. Reading the report

Example for `dave_1004.cpp`:

```text
File   : dave_1004.cpp
Student: Dave Mostafa (1004)

Problem 1
  Case 1:        PASSED   +1
  ...
  Problem 1 score: 10/10

Problem 2
  ...
  Problem 2 score: 0/10

Problem 3
  MISSING - no answer block for this problem
  Problem 3 score: 0/10

TOTAL SCORE: 10/30
Problem 2 failed - see work/dave_1004/p2.cpp
Problem 3 failed - no answer block was submitted
Artifacts kept in work/dave_1004
```

The hints after `TOTAL SCORE` only appear when at least one problem is not fully AC.

---

## 7. Work folders and cleanup

The judge uses `work/<student>/` for generated files such as `pN.cpp` and `pN.exe`.

| Result | What happens to `work/<student>/` |
|---|---|
| Every problem fully AC | Deleted. `work/` is removed too if it becomes empty. |
| Any problem fails: `CE`, `WA`, `RE`, `TLE`, `OLE`, partial, or `MISSING` | Kept for inspection. |
| Manual review error | No folder is created. |
| Unexpected judge error or Ctrl-C | Kept, and the path is printed before the error. |

When a problem fails, the judge prints:

```text
Problem N failed - see work/<student>/pN.cpp
Artifacts kept in work/<student>
```

For a missing block it prints:

```text
Problem N failed - no answer block was submitted
```

Kept folders remain until the same student is judged again or you delete them. To clear
all kept artifacts:

Windows `cmd`:

```cmd
rmdir /s /q work
```

Linux/macOS:

```bash
rm -rf work
```

`__pycache__/` folders are removed automatically when Python exits normally. Both
`work/` and `__pycache__/` are ignored by git.

---

## 8. Demo students and expected results

Run each demo file against `Testcases/demo.txt`.

| File | Scenario | Expected result |
|---|---|---|
| `alice_1001.cpp` | Everything correct, header without brackets | `TOTAL SCORE: 30/30` |
| `bob_1002.cpp` | `a - b` bug in Problem 2, infinite loop in Problem 3 | `11/30`; Problems 2 and 3 kept in `work/` |
| `carol_1003.cpp` | Compile error in Problem 1, `int` overflow in Problem 2, `best = 0` in Problem 3 | `14/30` |
| `dave_1004.cpp` | Star-prefixed answers, Problem 2 returns exit code 1, Problem 3 missing | `10/30` |
| `eve_1005.cpp` | Nested `/* */` breaks Problem 2 | `20/30` plus a stray-text warning |
| `frank_1006.cpp` | Header ID `9999` does not match file name ID `1006` | Manual review, exit code `2` |
| `grace_1007.cpp` | Header written with brackets | `TOTAL SCORE: 30/30` |
| `heidi_1008.cpp` | Line 1 is not the identification comment | Manual review, exit code `2` |

`Subtests/breakit/` contains extra samples for wrong file names, forbidden calls,
huge output, duplicate blocks, and old-style I/O.

---

## 9. Troubleshooting

### `g++` is not found

`g++ --version` must work in the same terminal that runs the judge.

- Windows: add the MinGW `bin` folder from Code::Blocks to `PATH`.
- Linux: install `g++` with your package manager.

### `FileNotFoundError` for `g++`

The compiler is not on `PATH`. Fix the installation before judging.

### Permission denied when running `pN.exe`

The build folder must be on a filesystem that allows execution. Avoid `noexec` mounts
for the project folder.

### Paths with spaces or `&`

Quote the path in the shell. The judge itself handles spaces in file paths.

### The testcase file is rejected

The error message lists every problem with its line number. Check:

- Cases are numbered 1 to 8 in order.
- Cases 7 and 8 are labeled `(Edge)`.
- Every case has one `Input:` and one `Output:`.
- Data lines do not accidentally equal `Problem N`, `Case N:`, `Input:`, or `Output:`.

### Manual review

Fix the header, file name, or forbidden code listed in the error message, then run
again.

### Everything was AC but `work/` is empty

That is expected. Work folders are removed after a fully correct run.

### `work/` still exists after a failed run

That is expected. Read the printed hint, inspect the kept files, then delete `work/`
when you are done.

### `CE` is printed

The first eight non-empty compiler lines are shown. Open the kept `pN.cpp` if the error
is not clear.

### `TLE` is printed

The case took longer than 2 seconds, usually because of an infinite loop or very slow
input handling.

---

## 10. Limitations

- One student file per run; there is no folder/batch mode.
- No sandbox. Student code runs with your user's permissions. Use a spare machine or a
  restricted account for untrusted submissions.
- No memory limit, even though the template mentions 256 MB.
- The run timeout is 2 seconds per case; the template says 1 second.
- Output comparison ignores only trailing spaces and trailing blank lines.
- `cin`/`cout`-only is a warning, not an enforced rule.
- A data line that exactly matches a section label is read as a label.
- There is no roster check and no CSV output; record scores manually.

---

## See also

- [Testcase format guide](testcase_format_guide.md) - how to write testcase files.
- [Developer guide](developer_guide.md) - internals, cleanup lifecycle, tests, and
  known risks.
- [Project README](../README.md) - quick start and project layout.
