# test_runner.py - automated checks for runner.py
import os

from config import WORK_DIR
from runner import judge_problem, normalize

BUILD = os.path.join(WORK_DIR, "_runner_test")
results = []


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    results.append(bool(condition))


def case(number, text_in, text_out, edge=False):
    return {
        "number": number,
        "edge": edge,
        "points": 2 if edge else 1,
        "input": text_in,
        "output": text_out,
    }


# 3 base cases (1 point each) + 1 edge case (2 points) = 5 points
CASES = [
    case(1, "2 3\n", "5\n"),
    case(2, "10 20\n", "30\n"),
    case(3, "0 0\n", "0\n"),
    case(4, "-5 5\n", "0\n", edge=True),
]

GOOD = """#include <iostream>
using namespace std;
int main() {
    long long a, b;
    cin >> a >> b;
    cout << a + b << endl;
    return 0;
}
"""

WRONG = GOOD.replace("a + b", "a - b")

ALWAYS_ZERO = """#include <iostream>
using namespace std;
int main() {
    cout << 0 << endl;
    return 0;
}
"""

BROKEN = "int main( {\n"

CRASH = GOOD.replace("return 0;", "return 1;")

FLOOD = """#include <iostream>
using namespace std;
int main() {
    long long n;
    cin >> n;
    while (true) cout << "spam\\n";
    return 0;
}
"""

FOREVER = """int main() {
    volatile int x = 0;
    while (true) { x = x + 1; }
    return 0;
}
"""

check("normalize strips trailing spaces and blank lines",
      normalize("a  \r\nb\n\n\n") == ["a", "b"])

r = judge_problem(GOOD, CASES, BUILD, "good")
check("good solution: AC, 4/4 cases, 5/5 points",
      r["status"] == "AC" and r["passed"] == 4 and r["score"] == 5 and r["max_score"] == 5)

r = judge_problem(WRONG, CASES, BUILD, "wrong")
check("wrong solution: PARTIAL, verdicts WA WA AC WA, 1 point",
      r["status"] == "PARTIAL" and r["verdicts"] == ["WA", "WA", "AC", "WA"] and r["score"] == 1)

r = judge_problem(ALWAYS_ZERO, CASES, BUILD, "zero")
check("edge case is worth 2 points: verdicts WA WA AC AC, 3 points",
      r["verdicts"] == ["WA", "WA", "AC", "AC"] and r["score"] == 3)

r = judge_problem(BROKEN, CASES, BUILD, "broken")
check("compile error: status CE, 0 points", r["status"] == "CE" and r["score"] == 0)

r = judge_problem(CRASH, CASES, BUILD, "crash")
check("runtime error: RE on all cases", r["verdicts"] == ["RE"] * 4)

r = judge_problem(FLOOD, CASES, BUILD, "flood")
check("output flood: OLE on all cases, 0 points",
      r["verdicts"] == ["OLE"] * 4 and r["score"] == 0)

print("(next check waits for 4 timeouts, about 8 seconds)")
r = judge_problem(FOREVER, CASES, BUILD, "forever")
check("infinite loop: TLE on all cases, 0 points", r["verdicts"] == ["TLE"] * 4 and r["score"] == 0)

print()
print("%d / %d checks passed" % (sum(results), len(results)))
if not all(results):
    raise SystemExit(1)