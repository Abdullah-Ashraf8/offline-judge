# Next Steps: Shared Judging Core, Batch Mode, and CSV

Status: planned, not implemented.

Part 0 is already complete: the six `test_*.py` files were moved to `Dev_Tests/` and
are run from the project root with `python3 -m Dev_Tests.test_*`.

This document covers the remaining work: Parts A, B, and C.

---

## Locked decisions

- Batch command: `python batch.py <submissions_dir> <testcase_file.txt>`
- Default CSV: `results/<testcase_stem>.csv`
- Default assignment name: testcase file stem
- Manual-review rows: blank `auto_score`, batch exits `2`
- Console output: one summary line per student; `--verbose` prints full reports
- Processing: sequential, non-recursive, direct `*.cpp` files only
- Platforms: Windows and Linux/macOS equally supported
- Kept `work/<student>/` behavior stays exactly as it is today

Out of scope: `--jobs`, recursive mode, roster validation, sandboxing, memory limits,
parallel grading, per-student report files.

---

## Part A - Extract reusable judging core

### Goal

Make the single-file judging logic callable from both `judge.py` and the future batch
runner without changing the existing single-file CLI behavior.

### Files

- Modify `judge.py`
- Verify with `Dev_Tests/test_judge.py` and the other existing tests

### Changes

1. Split `main()` into:
   - `judge_submission(assignment_path, tests, say=print)`
   - `main()`

2. `judge_submission` keeps the current behavior:
   - extract the header and answer blocks
   - raise `ManualReviewError` when manual review is needed
   - print through the supplied `say` callback
   - compile and judge every problem
   - apply the existing work-folder retention rules
   - return a structured result

3. Proposed result:

```python
{
    "header": {"name": "...", "email": "...", "student_id": "..."},
    "numbers": [1, 2, 3],
    "failed": [2, 3],
    "total": 11,
    "max_total": 30,
    "all_ok": False,
    "kept_dir": "work/bob_1002",
}
```

4. Attach the parsed header to `ManualReviewError` so batch mode can fill
   `student_id` and `name` even when a file needs review.

5. Add a compiler preflight:
   - use `shutil.which(config.COMPILER)`
   - print a clear error and exit `1` if `g++` is missing
   - avoid an uncaught `FileNotFoundError`

6. Keep these unchanged:
   - report text
   - warnings and hints
   - work-folder deletion/retention
   - exit codes `0`, `1`, and `2`

### Tests

Run from the project root:

```bash
python3 -m Dev_Tests.test_judge
python3 -m Dev_Tests.test_extractor
python3 -m Dev_Tests.test_testcases
python3 -m Dev_Tests.test_runner
python3 -m Dev_Tests.test_safety
python3 -m Dev_Tests.test_cleanup
```

Also compare the manual `alice` and `dave` output before and after the refactor.

Expected:

- `alice`: `30/30`, no kept work folder
- `dave`: `10/30`, kept work folder and hints
- all six test modules pass
- no leftover `work/` or `__pycache__/`

### Suggested commit

`Extract reusable submission judging core`

---

## Part B - Add batch grading mode with CSV

### Goal

Grade a whole folder of submissions with one command and write a score CSV.

### Files

- Add `batch.py`
- Add `Dev_Tests/test_batch.py`

### Command

```bash
python3 batch.py <submissions_dir> <testcase_file.txt> [options]
```

Options:

```text
--csv PATH          CSV output path
--assignment NAME   Value for the assignment column
--verbose           Print the full report for each student
```

Defaults:

- `--csv`: `results/<testcase_stem>.csv`
- `--assignment`: `<testcase_stem>`

### Behavior

1. Validate the submissions folder and testcase file.
2. Check that `g++` is available.
3. Parse the testcase file once.
4. Process `*.cpp` files directly in the folder, sorted by filename.
5. Run each student through `judge_submission`.
6. Catch `ManualReviewError` per student and continue the batch.
7. Catch unexpected per-student errors, report them, and continue.
8. Keep using the existing work-folder retention rules.
9. Create the CSV output directory if needed.
10. Overwrite an existing CSV output file.

### Console output

Default: one line per student.

```text
alice_1001.cpp  1001  Alice Hassan   AC       30/30
bob_1002.cpp    1002  Bob Samir      PARTIAL  11/30
frank_1006.cpp  -     -               REVIEW   -
```

With `--verbose`, print the existing full judge report per student before the summary
line.

End the run with counts and the CSV path:

```text
Students: 8   Auto-scored: 6   Manual review: 2   Errors: 0
CSV written to results/demo.csv
```

### CSV format

Exactly these columns, in this order:

```text
student_id,name,assignment,auto_score
1001,Alice Hassan,demo,30
1002,Bob Samir,demo,11
1006,,demo,
```

Rules:

- Use the `csv` module with UTF-8 and `newline=""`.
- `auto_score` is the student total for auto-scored files.
- `auto_score` is blank for manual review.
- Use the parsed header for name/ID when available.
- Fall back to the filename stem when the header is unusable.

### Exit codes

- `0`: all students were auto-scored
- `2`: at least one manual review, no fatal errors
- `1`: usage, testcase, compiler, CSV, or unexpected grading error

### Tests

Add `Dev_Tests/test_batch.py`:

1. Create a temporary submissions folder.
2. Copy `alice_1001.cpp`, `dave_1004.cpp`, and `frank_1006.cpp` into it.
3. Run the real `batch.py` CLI with an explicit `--csv`.
4. Check the exit code is `2`.
5. Check the CSV header and rows:
   - alice: `30`
   - dave: `10`
   - frank: blank
6. Check the summary lines.
7. Check that dave's work folder is kept and alice's is deleted.
8. Check `--assignment` and `--verbose`.
9. Clean up all temporary files and test work folders.

Run:

```bash
python3 -m Dev_Tests.test_batch
```

### Review points

- CSV opens correctly on Windows and Linux.
- One bad student does not stop the batch.
- Work retention matches single-file mode.
- Manual review is visible in both console and CSV.
- No duplicate work folders are created.

### Suggested commit

`Add batch grading mode with CSV output`

---

## Part C - Document batch grading

### Files

- `README.md`
- `Docs/offline_judge_user_guide.md`
- `Docs/developer_guide.md`

### README

- Add a batch quick-start command.
- Show the CSV location and columns.
- Mention `--verbose`.
- Add `Dev_Tests/test_batch` to the test commands.

### User guide

Add a "Batch grading" section covering:

- The command and options.
- CSV columns and where the file is written.
- Blank score for manual review.
- Exit codes `0`, `1`, and `2`.
- Summary versus `--verbose`.
- Kept `work/` folders after failed students.
- The fact that processing is sequential and non-recursive.

### Developer guide

Document:

- `judge_submission` and the shared result structure.
- The `batch.py` flow.
- Why testcases are parsed once.
- CSV writing and encoding rules.
- Why batch is sequential in the first version.
- Future `--jobs` as explicitly out of scope for now.

### Tests

Re-run the full suite from the project root:

```bash
python3 -m Dev_Tests.test_extractor
python3 -m Dev_Tests.test_testcases
python3 -m Dev_Tests.test_runner
python3 -m Dev_Tests.test_safety
python3 -m Dev_Tests.test_cleanup
python3 -m Dev_Tests.test_judge
python3 -m Dev_Tests.test_batch
```

### Suggested commit

`Document batch grading and CSV output`

---

## Final verification

```bash
python3 judge.py Subtests/demo/alice_1001.cpp Testcases/demo.txt
python3 batch.py Subtests/demo Testcases/demo.txt --csv /tmp/demo.csv --verbose
```

Check:

- single-file output is unchanged
- batch exits `2` for the demo folder because of the manual-review files
- CSV contains every student
- failed students keep their work folders
- no `__pycache__` remains afterward

## Implementation order

1. Part A
2. Part B
3. Part C

Stop after each part for review and commit. No commits or pushes are made
automatically.
