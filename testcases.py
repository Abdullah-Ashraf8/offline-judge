# testcases.py - reads the single testcase file of one assignment
# Format reference: judge_formats.md, section 2
import re

import config

PROBLEM_RE = re.compile(r"^\s*Problem\s+(\d+)\s*$", re.IGNORECASE)
CASE_RE = re.compile(r"^\s*Case\s+(\d+)\s*(\(\s*Edge\s*\))?\s*:\s*$", re.IGNORECASE)
INPUT_RE = re.compile(r"^\s*Input\s*:\s*$", re.IGNORECASE)
OUTPUT_RE = re.compile(r"^\s*Output\s*:\s*$", re.IGNORECASE)


def _strip_trailing_blank(lines):
    while lines and not lines[-1].strip():
        lines.pop()
    return lines


def parse_testcases(path):
    """Return {problem_number: [case, ...]}.
    Each case is {"number", "edge", "points", "input", "output"}.
    Raises ValueError with one line per format error."""
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        lines = f.read().replace("\r\n", "\n").split("\n")

    errors = []
    raw = {}
    problem = None
    case = None
    mode = None

    for lineno, line in enumerate(lines, start=1):
        line = line.rstrip()

        m = PROBLEM_RE.match(line)
        if m:
            problem = int(m.group(1))
            if problem in raw:
                errors.append("line %d: Problem %d appears twice" % (lineno, problem))
            raw[problem] = []
            case = None
            mode = None
            continue

        m = CASE_RE.match(line)
        if m:
            if problem is None:
                errors.append("line %d: Case before any Problem line" % lineno)
                continue
            case = {
                "number": int(m.group(1)),
                "edge": m.group(2) is not None,
                "input": [],
                "output": [],
                "has_input": False,
                "has_output": False,
            }
            raw[problem].append(case)
            mode = None
            continue

        if INPUT_RE.match(line):
            if case is None:
                errors.append("line %d: Input: outside a case" % lineno)
            elif case["has_input"]:
                errors.append("line %d: second Input: in the same case" % lineno)
            else:
                case["has_input"] = True
                mode = "input"
            continue

        if OUTPUT_RE.match(line):
            if case is None:
                errors.append("line %d: Output: outside a case" % lineno)
            elif case["has_output"]:
                errors.append("line %d: second Output: in the same case" % lineno)
            else:
                case["has_output"] = True
                mode = "output"
            continue

        if mode == "input":
            case["input"].append(line)
        elif mode == "output":
            case["output"].append(line)
        elif line.strip():
            errors.append("line %d: unexpected text: %s" % (lineno, line.strip()[:40]))

    total_cases = config.BASE_CASE_COUNT + config.EDGE_CASE_COUNT
    problems = {}
    for number, cases in raw.items():
        numbers = [c["number"] for c in cases]
        if numbers != list(range(1, total_cases + 1)):
            errors.append(
                "Problem %d: cases must be numbered 1 to %d in order, found %s"
                % (number, total_cases, numbers)
            )
        final = []
        for c in cases:
            label = "Problem %d Case %d" % (number, c["number"])
            should_be_edge = c["number"] > config.BASE_CASE_COUNT
            if c["edge"] != should_be_edge:
                if should_be_edge:
                    errors.append("%s: must be written 'Case N (Edge):'" % label)
                else:
                    errors.append("%s: must be written 'Case N:'" % label)
            if not c["has_input"]:
                errors.append("%s: missing Input:" % label)
            if not c["has_output"]:
                errors.append("%s: missing Output:" % label)
            case_in = _strip_trailing_blank(c["input"])
            case_out = _strip_trailing_blank(c["output"])
            if c["has_output"] and not case_out:
                errors.append("%s: Output is empty" % label)
            final.append(
                {
                    "number": c["number"],
                    "edge": c["edge"],
                    "points": config.EDGE_POINTS if c["edge"] else config.BASE_POINTS,
                    "input": "\n".join(case_in) + "\n",
                    "output": "\n".join(case_out) + "\n",
                }
            )
        problems[number] = final

    if not problems and not errors:
        errors.append("no 'Problem N' sections found")
    if errors:
        raise ValueError("\n".join(errors))
    return problems