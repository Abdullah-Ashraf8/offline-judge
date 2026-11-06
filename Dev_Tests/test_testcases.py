# test_testcases.py - automated checks for testcases.py
import os
import tempfile

import cleanup
from config import TESTS_DIR
from testcases import parse_testcases

DEMO = os.path.join(TESTS_DIR, "demo.txt")
results = []


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    results.append(bool(condition))


def valid_text():
    """A correct one-problem testcase file: 6 base cases and 2 edge cases."""
    parts = ["Problem 1"]
    for n in range(1, 9):
        label = ("Case %d (Edge):" % n) if n > 6 else ("Case %d:" % n)
        parts += [label, "Input:", str(n), "Output:", str(n * 2)]
    return "\n".join(parts) + "\n"


def parse_text(text, newline="\n"):
    handle, path = tempfile.mkstemp(suffix=".txt")
    os.close(handle)
    try:
        with open(path, "w", encoding="utf-8", newline=newline) as f:
            f.write(text)
        return parse_testcases(path)
    finally:
        os.remove(path)


def error_of(text):
    """Return the error message for a bad file, or '' if it parsed fine."""
    try:
        parse_text(text)
    except ValueError as error:
        return str(error)
    return ""


demo = parse_testcases(DEMO)
check("demo: problems 1, 2, 3 found", sorted(demo) == [1, 2, 3])
check("demo: every problem has 8 cases worth 10 points in total",
      all(len(demo[n]) == 8 and sum(c["points"] for c in demo[n]) == 10 for n in demo))
check("demo: cases 1-6 are base (1 point), cases 7-8 are edge (2 points)",
      all(c["edge"] == (c["number"] > 6) and c["points"] == (2 if c["edge"] else 1)
          for n in demo for c in demo[n]))
check("demo: multi-line input kept", demo[3][0]["input"] == "3\n1 9 4\n")
check("demo: large expected output kept", demo[1][7]["output"] == "6000000000\n")

text = valid_text()
good = parse_text(text)
check("generated file: 8 cases, case 3 has input 3 and output 6",
      len(good[1]) == 8 and good[1][2]["input"] == "3\n" and good[1][2]["output"] == "6\n")
check("Windows line endings give the same result", parse_text(text, "\r\n") == good)

check("missing Output: is reported",
      "missing Output" in error_of(text.replace("Output:\n8\n", "", 1)))
check("empty Output is reported",
      "Output is empty" in error_of(text.replace("Output:\n8\n", "Output:\n", 1)))
check("only 7 cases is reported",
      "numbered 1 to 8" in error_of(text.split("Case 8 (Edge):")[0]))
check("edge case without (Edge) label is reported",
      "Edge" in error_of(text.replace("Case 7 (Edge):", "Case 7:")))
check("text before the first Problem line is reported",
      "unexpected text" in error_of("hello\n" + text))

print()
print("%d / %d checks passed" % (sum(results), len(results)))
if not all(results):
    raise SystemExit(1)