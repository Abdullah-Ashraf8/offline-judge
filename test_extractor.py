# test_extractor.py - automated checks for extractor.py
import os
import tempfile

import cleanup
from config import SUBMISSIONS_DIR
from extractor import extract_submission, filename_id

DEMO_DIR = os.path.join(SUBMISSIONS_DIR, "demo")
results = []


def load(filename):
    return extract_submission(os.path.join(DEMO_DIR, filename))


def from_text(text):
    """Write text to a temporary .cpp file and extract it."""
    handle, path = tempfile.mkstemp(suffix=".cpp")
    os.close(handle)
    try:
        with open(path, "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
        return extract_submission(path)
    finally:
        os.remove(path)


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    results.append(bool(condition))


# ---- alice: perfect file ----
alice = load("alice_1001.cpp")
h = alice["header"]
check("alice: header parsed",
      h["name"] == "Alice Hassan" and h["email"] == "alice@example.com"
      and h["student_id"] == "1001")
check("alice: header accepted", alice["header_error"] == "")
check("alice: problems 1,2,3 found", sorted(alice["problems"]) == [1, 2, 3])
check("alice: no warnings", alice["warnings"] == [])
p1 = alice["problems"][1]
check("alice: title and separator removed",
      "Problem 1" not in p1 and "-----" not in p1)
check("alice: code kept intact",
      p1.startswith("#include <iostream>") and "cout << n * 2" in p1)

# ---- bob, carol ----
check("bob: problems 1,2,3 found", sorted(load("bob_1002.cpp")["problems"]) == [1, 2, 3])
carol = load("carol_1003.cpp")
check("carol: problems 1,2,3 found", sorted(carol["problems"]) == [1, 2, 3])
check("carol: compile-error line preserved", "cin >> n\n" in carol["problems"][1])

# ---- dave: star-prefixed lines, problem 3 missing ----
dave = load("dave_1004.cpp")
dh = dave["header"]
check("dave: header parsed",
      dh["name"] == "Dave Mostafa" and dh["email"] == "dave@example.com"
      and dh["student_id"] == "1004" and dave["header_error"] == "")
check("dave: problems 1,2 found and 3 absent", sorted(dave["problems"]) == [1, 2])
dp1 = dave["problems"][1]
check("dave: star prefixes removed",
      dp1.startswith("#include <iostream>")
      and not any(l.lstrip().startswith("*") for l in dp1.split("\n")))

# ---- eve: nested comment ----
eve = load("eve_1005.cpp")
check("eve: header accepted", eve["header_error"] == "")
check("eve: stray text detected", any("stray text" in w for w in eve["warnings"]))
check("eve: nested comment truncates problem 2",
      eve["problems"][2].rstrip().endswith("/* the two numbers"))
check("eve: problem 3 still found", 3 in eve["problems"])

# ---- grace, frank, heidi: header variants ----
grace = load("grace_1007.cpp")["header"]
check("grace: brackets removed from header",
      grace["name"] == "Grace Omar" and grace["email"] == "grace@example.com"
      and grace["student_id"] == "1007")
check("frank: header ID read as 9999", load("frank_1006.cpp")["header"]["student_id"] == "9999")
check("heidi: non-identification first line detected",
      load("heidi_1008.cpp")["header_error"] == "first line is not the identification comment")

# ---- filename_id ----
check("filename_id: underscore inside the name", filename_id("Hassan_Ahmed_PS001.cpp") == "PS001")
check("filename_id: simple name", filename_id("alice_1001.cpp") == "1001")
check("filename_id: no underscore", filename_id("nounderscore.cpp") == "")

# ---- synthetic files ----
r = from_text("// Name:[your full name]  Email:[your email]  Student ID:[your ID]\n")
check("unfilled template rejected",
      r["header_error"].startswith("header line has empty or unfilled fields"))

r = from_text("// Name:Hassan Ahmed  Email:h@x.com  Student ID:PS001\n"
              "/* Problem 1\n int main(){}\n */\n")
check("filled header without brackets accepted",
      r["header"]["name"] == "Hassan Ahmed" and r["header"]["student_id"] == "PS001"
      and r["header_error"] == "" and sorted(r["problems"]) == [1] and r["warnings"] == [])

r = from_text("// Name:Sam  Email:[your email]  Student ID:S1\n")
check("partly filled header: email flagged", "email" in r["header_error"])

check("empty file reported", from_text("")["header_error"] == "file is empty")

print()
print("%d / %d checks passed" % (sum(results), len(results)))
if not all(results):
    raise SystemExit(1)