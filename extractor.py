# extractor.py - reads one student .cpp file and pulls out:
#   - the identification comment on line 1 (name, email, student ID)
#   - one code block per problem
#   - a list of warnings about format problems
# Format reference: judge_formats.md, section 1
import os
import re

BLOCK_RE = re.compile(r"/\*(.*?)\*/", re.DOTALL)
PROBLEM_RE = re.compile(r"^\s*\*?\s*Problem\s*#?\s*(\d+)", re.IGNORECASE)
DASH_RE = re.compile(r"^\s*\*?\s*[-=_]{3,}\s*$")

HEADER_RE = re.compile(
    r"^\s*//\s*Name\s*:(?P<name>.*?)Email\s*:(?P<email>.*?)Student\s*ID\s*:(?P<id>.*)$",
    re.IGNORECASE,
)

# template text a student may leave unchanged
PLACEHOLDERS = {
    "name": "your full name",
    "email": "your email",
    "student_id": "your id",
}


def _clean(value, placeholder):
    """Trim, drop one pair of [brackets], and treat template text as empty."""
    v = value.strip()
    if v.startswith("[") and v.endswith("]"):
        v = v[1:-1].strip()
    if v.lower() == placeholder:
        return ""
    return v


def _parse_header(first_line):
    """Return (header_dict, error_text). error_text is empty when the header is fine."""
    header = {"name": "", "email": "", "student_id": ""}
    m = HEADER_RE.match(first_line)
    if not m:
        return header, "first line is not the identification comment"
    header["name"] = _clean(m.group("name"), PLACEHOLDERS["name"])
    header["email"] = _clean(m.group("email"), PLACEHOLDERS["email"])
    header["student_id"] = _clean(m.group("id"), PLACEHOLDERS["student_id"])
    missing = [key for key, value in header.items() if not value]
    if missing:
        return header, "header line has empty or unfilled fields: " + ", ".join(missing)
    return header, ""


def filename_id(filename):
    """ID part of 'Name_ID.cpp': the text after the last underscore ('' if none)."""
    stem = os.path.splitext(os.path.basename(filename))[0]
    if "_" not in stem:
        return ""
    return stem.rsplit("_", 1)[1]


def _strip_star_prefix(lines):
    """If EVERY non-blank line starts with '*', remove one '*' (and one space)."""
    nonblank = [l for l in lines if l.strip()]
    if not nonblank or not all(l.lstrip().startswith("*") for l in nonblank):
        return lines
    out = []
    for l in lines:
        s = l.lstrip()
        if s.startswith("*"):
            s = s[1:]
            if s.startswith(" "):
                s = s[1:]
            out.append(s)
        else:
            out.append(l)
    return out


def _parse_problem_block(body):
    """Return (problem_number, code) or None if this block is not a problem block."""
    lines = body.split("\n")
    first = next((i for i, l in enumerate(lines) if l.strip()), None)
    if first is None:
        return None
    m = PROBLEM_RE.match(lines[first])
    if not m:
        return None
    number = int(m.group(1))

    rest = lines[first + 1:]
    nxt = next((i for i, l in enumerate(rest) if l.strip()), None)
    if nxt is not None and DASH_RE.match(rest[nxt]):
        rest = rest[nxt + 1:]

    rest = _strip_star_prefix(rest)
    code = "\n".join(rest).strip("\n").rstrip() + "\n"
    return number, code


def extract_submission(path):
    with open(path, "r", encoding="utf-8-sig", errors="replace") as f:
        text = f.read()

    result = {
        "header": {"name": "", "email": "", "student_id": ""},
        "header_error": "",
        "problems": {},
        "warnings": [],
    }

    lines = text.splitlines()
    if not lines:
        result["header_error"] = "file is empty"
    else:
        result["header"], result["header_error"] = _parse_header(lines[0])

    for body in BLOCK_RE.findall(text):
        parsed = _parse_problem_block(body)
        if parsed is None:
            continue
        number, code = parsed
        if number in result["problems"]:
            result["warnings"].append("duplicate problem %d (kept first)" % number)
            continue
        if not code.strip():
            result["warnings"].append("problem %d block is empty" % number)
            continue
        result["problems"][number] = code

    # anything left outside comments means the format was broken
    # (for example a nested */ ended a block early)
    leftover = BLOCK_RE.sub("", text)
    leftover = re.sub(r"//[^\n]*", "", leftover)
    if leftover.strip():
        result["warnings"].append("stray text outside comment blocks")

    return result


if __name__ == "__main__":
    import sys

    if len(sys.argv) != 2:
        print("usage: python extractor.py <file.cpp>")
        raise SystemExit(1)

    data = extract_submission(sys.argv[1])
    print("HEADER      :", data["header"])
    print("HEADER ERROR:", data["header_error"] if data["header_error"] else "none")
    print("WARNINGS    :", data["warnings"] if data["warnings"] else "none")
    for number in sorted(data["problems"]):
        print("\n--- Problem %d ---" % number)
        print(data["problems"][number])