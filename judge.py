# judge.py - judge ONE student file against ONE testcase file
# usage:   python judge.py <assignment_file.cpp> <testcase_file.txt>
# example: python judge.py submissions\demo\alice_1001.cpp tests\demo.txt
# exit codes: 0 = judged, 1 = usage or file problem, 2 = file needs manual review
import os
import shutil
import sys

import config
from extractor import extract_submission, filename_id
from runner import judge_problem
from safety import find_forbidden, find_style_warnings
from testcases import parse_testcases

HEADER_FIX = "line 1 must be: // Name:[your full name]  Email:[your email]  Student ID:[your ID]"


class ManualReviewError(Exception):
    """The file cannot be auto-scored; a human must fix or review it."""


def say(text=""):
    print(text, flush=True)


def check_manual_review(path, data):
    """Raise ManualReviewError listing every problem found in the file."""
    name = os.path.basename(path)
    issues = []  # (reason, fix) pairs

    if data["header_error"]:
        issues.append((data["header_error"], HEADER_FIX))
    elif config.CHECK_FILENAME_ID:
        file_id = filename_id(name)
        header_id = data["header"]["student_id"]
        if not file_id:
            issues.append((
                "filename does not follow Name_ID.cpp",
                "rename the file to <Name>_<StudentID>.cpp",
            ))
        elif file_id.lower() != header_id.lower():
            issues.append((
                "filename ID '%s' does not match header ID '%s'" % (file_id, header_id),
                "rename the file to <Name>_<StudentID>.cpp or correct the Student ID on line 1",
            ))

    for number in sorted(data["problems"]):
        found = find_forbidden(data["problems"][number])
        if found:
            issues.append((
                "Problem %d uses forbidden call(s): %s" % (number, ", ".join(found)),
                "remove those calls from Problem %d and resubmit" % number,
            ))

    if issues:
        reason = "; ".join(r for r, _ in issues)
        fix = "; ".join(f for _, f in issues)
        raise ManualReviewError(
            "this file needs manual review: %s - %s. To fix: %s" % (name, reason, fix)
        )


def main():
    if len(sys.argv) != 3:
        say("usage: python judge.py <assignment_file.cpp> <testcase_file.txt>")
        say("example: python judge.py submissions\\demo\\alice_1001.cpp tests\\demo.txt")
        return 1

    assignment_path = sys.argv[1]
    tests_path = sys.argv[2]

    if not os.path.isfile(assignment_path):
        say("assignment file not found: " + assignment_path)
        return 1
    if not os.path.isfile(tests_path):
        say("testcase file not found: " + tests_path)
        return 1

    try:
        tests = parse_testcases(tests_path)
    except ValueError as error:
        say("testcase file has errors:")
        say(str(error))
        return 1

    data = extract_submission(assignment_path)
    check_manual_review(assignment_path, data)  # raises ManualReviewError

    header = data["header"]
    numbers = sorted(tests)
    max_total = sum(c["points"] for n in numbers for c in tests[n])

    say("File   : " + os.path.basename(assignment_path))
    say("Student: %s (%s)" % (header["name"], header["student_id"]))
    for w in data["warnings"]:
        say("WARNING: " + w)
    for number in sorted(data["problems"]):
        style = find_style_warnings(data["problems"][number])
        if style:
            say("WARNING: Problem %d uses %s (spec: use cin and cout only)"
                % (number, ", ".join(style)))
    say()

    stem = os.path.splitext(os.path.basename(assignment_path))[0]
    build_dir = os.path.join(config.WORK_DIR, stem)
    if os.path.isdir(build_dir):
        shutil.rmtree(build_dir, ignore_errors=True)
    os.makedirs(build_dir, exist_ok=True)

    total = 0
    for n in numbers:
        cases = tests[n]
        max_score = sum(c["points"] for c in cases)
        say("Problem %d" % n)

        if n not in data["problems"]:
            say("  MISSING - no answer block for this problem")
            say("  Problem %d score: 0/%d" % (n, max_score))
            say()
            continue

        res = judge_problem(data["problems"][n], cases, build_dir, "p%d" % n)

        if res["status"] == "CE":
            say("  COMPILE ERROR - all cases failed")
            lines = [l.strip() for l in res["note"].splitlines() if l.strip()]
            for line in lines[:8]:
                say("    " + line)

        for case, verdict in zip(cases, res["verdicts"]):
            label = "Case %d%s:" % (case["number"], " (Edge)" if case["edge"] else "")
            if verdict == "AC":
                say("  %-14s PASSED   +%d" % (label, case["points"]))
            else:
                say("  %-14s FAILED   +0 of %d  [%s]" % (label, case["points"], verdict))

        say("  Problem %d score: %d/%d" % (n, res["score"], max_score))
        say()
        total += res["score"]

    say("TOTAL SCORE: %d/%d" % (total, max_total))
    return 0


if __name__ == "__main__":
    try:
        code = main()
    except ManualReviewError as error:
        print("ERROR: " + str(error), file=sys.stderr, flush=True)
        code = 2
    raise SystemExit(code)