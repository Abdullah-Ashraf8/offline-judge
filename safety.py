# safety.py - checks a student's answer code before it is run
# Used by judge.py. Format reference: judge_formats.md
# This is a screen, not a sandbox: it sends suspicious code to manual review.
import re

# calls that start programs, delete files or open the network
FORBIDDEN_CALLS = [
    "system", "popen", "pclose", "fork", "execl", "execle", "execlp",
    "execv", "execve", "execvp", "CreateProcess", "WinExec", "ShellExecute",
    "remove", "unlink", "rmdir", "_unlink", "_rmdir", "_wsystem",
    "LoadLibrary", "socket", "connect", "kill",
]

# headers that give access to the system, processes, sockets or files
FORBIDDEN_HEADERS = [
    "windows.h", "unistd.h", "process.h", "winsock2.h", "sys/socket.h",
    "dirent.h", "fstream", "filesystem",
]

# old-style I/O: allowed by the program, but the spec says cin and cout only
STYLE_WARNING_CALLS = ["scanf", "printf", "puts", "gets", "getchar"]

_STRING_RE = re.compile(r'"(?:\\.|[^"\\\n])*"|\'(?:\\.|[^\'\\\n])*\'')
_LINE_COMMENT_RE = re.compile(r"//[^\n]*")


def _strip_literals_and_comments(code):
    """Remove string and character literals first, then // comments."""
    code = _STRING_RE.sub('""', code)
    return _LINE_COMMENT_RE.sub("", code)


def find_forbidden(code):
    """Return a sorted list of forbidden items found in code (empty if none)."""
    found = set()
    stripped = _strip_literals_and_comments(code)
    for name in FORBIDDEN_CALLS:
        if re.search(r"\b%s\s*\(" % re.escape(name), stripped):
            found.add(name + "()")
    for header in FORBIDDEN_HEADERS:
        if re.search(r'#\s*include\s*[<"]%s[>"]' % re.escape(header), code):
            found.add("#include <%s>" % header)
    for word in ("asm", "__asm__"):
        if re.search(r"\b%s\b" % word, stripped):
            found.add(word)
    return sorted(found)


def find_style_warnings(code):
    """Return a sorted list of old-style I/O calls used in code."""
    stripped = _strip_literals_and_comments(code)
    return sorted(
        name for name in STYLE_WARNING_CALLS
        if re.search(r"\b%s\s*\(" % name, stripped)
    )