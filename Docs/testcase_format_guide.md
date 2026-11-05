# Testcase Format Guide

This guide explains how to write the plain-text testcase files the judge reads. Put them
in `Testcases/`; `Testcases/demo.txt` is the working example.

The format is strict. `testcases.py` validates the whole file before any student code is
compiled, so a malformed testcase file stops the run with line-numbered errors.

---

## 1. Rules

### Problem sections

- Each problem starts with `Problem N` on its own line, for example `Problem 1`.
- Problems can appear in any order, but should normally be written 1, 2, 3, ...
- A problem cannot appear twice.
- A file with no `Problem` section is invalid.

### Cases

By default every problem must have exactly **8 cases**, numbered 1 to 8 in order.
The counts come from `config.py`:

| Setting | Default | Meaning |
|---|---|---|
| `BASE_CASE_COUNT` | `6` | Cases 1 to 6 |
| `EDGE_CASE_COUNT` | `2` | Cases 7 and 8 |
| `BASE_POINTS` | `1` | Points per base case |
| `EDGE_POINTS` | `2` | Points per edge case |

So the default maximum is `6 * 1 + 2 * 2 = 10` points per problem.

Case labels:

- Cases 1 to 6 are written `Case N:`.
- Cases 7 and 8 **must** be written `Case N (Edge):`.
- A missing `(Edge)` label, or an extra one on a base case, is a validation error.
- Cases must be numbered `1, 2, 3, ...` with no gaps and no duplicates.

### Input and Output

Every case needs exactly one `Input:` line and one `Output:` line:

```text
Case 1:
Input:
10 20
Output:
30
```

- Data lines after `Input:` belong to the input until `Output:` or the next case label.
- The output cannot be empty.
- Input may be empty; the judge sends a single newline in that case.
- Blank lines inside a block are kept. Trailing blank lines are trimmed.
- The file may use Windows (`CRLF`) or Unix (`LF`) line endings.

### Output comparison

The judge accepts an answer when the output matches after:

- removing trailing spaces from each line, and
- removing blank lines at the very end.

Everything else must match exactly: casing, punctuation, spaces between values, and the
number of lines all matter.

### Do not use labels as data

A line that is exactly `Problem N`, `Case N:`, `Input:`, or `Output:` is read as a
section label, even if it is indented or has trailing spaces. Do not use those exact
lines as actual input or expected output.

---

## 2. Example testcase file

A complete problem with six base cases and two edge cases:

```text
Problem 1
Case 1:
Input:
10 20
Output:
30

Case 2:
Input:
15 5
Output:
20

Case 3:
Input:
100 200
Output:
300

Case 4:
Input:
1 1
Output:
2

Case 5:
Input:
99 1
Output:
100

Case 6:
Input:
50 50
Output:
100

Case 7 (Edge):
Input:
-5 5
Output:
0

Case 8 (Edge):
Input:
0 0
Output:
0
```

To add the next problem, start a new `Problem 2` section and repeat the same eight-case
structure.

---

## 3. Common mistakes

| Mistake | Result |
|---|---|
| Seven cases instead of eight | `cases must be numbered 1 to 8 in order` |
| Case 7 written `Case 7:` | `must be written 'Case N (Edge):'` |
| Case 3 written `(Edge)` | `must be written 'Case N:'` |
| Missing `Input:` | `missing Input:` |
| Missing `Output:` | `missing Output:` |
| Empty output | `Output is empty` |
| Text before the first problem | `unexpected text` with the line number |
| `Input:` before any case | `Input: outside a case` |
| Two `Input:` lines in one case | `second Input: in the same case` |
| Duplicate `Problem 1` | `Problem 1 appears twice` |
| Data line equal to `Output:` | Read as a label instead of data |

Run the parser by itself when editing a testcase file:

```bash
python3 test_testcases.py
```

---

## 4. Writing good cases

1. Cover the normal cases first: small values, larger values, and typical edge values
   such as zero and negative numbers.
2. Use cases 7 and 8 for hidden edge cases: minimum/maximum values, empty input,
   repeated values, and boundary conditions.
3. Verify every expected output with a trusted reference solution or brute-force
   program. Do not type expected outputs by hand when the problem is non-trivial.
4. Keep the file clean: one blank line between cases is fine, but no commentary text
   inside the file unless it is inside an input/output block.
5. Use the exact problem numbers used by the student submission and the assignment.

---

## 5. Changing the number of cases or points

The defaults live in `config.py`. If you change them, update every testcase file to the
new count and update the checks in `test_testcases.py`; the judge validates the exact
configured number of cases, and the self-tests assert the default 6 + 2 layout.

The student-facing rules are in the
[user guide](offline_judge_user_guide.md#4-step-by-step-flow).
