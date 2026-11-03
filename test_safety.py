# test_safety.py - automated checks for safety.py
from safety import find_forbidden, find_style_warnings

results = []


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    results.append(bool(condition))


CLEAN = """#include <iostream>
using namespace std;
int main() {
    long long n;
    cin >> n;
    cout << n * 2 << endl;
    return 0;
}
"""

check("system() call is found",
      find_forbidden('int main(){ system("dir"); }') == ["system()"])
check("std::system() call is found",
      find_forbidden('int main(){ std::system("dir"); }') == ["system()"])
check("word inside a string literal is ignored",
      find_forbidden('int main(){ cout << "call system(x)"; }') == [])
check("word inside a // comment is ignored",
      find_forbidden("// remove(x)\nint main(){}") == [])
check("windows.h include is found",
      find_forbidden("#include <windows.h>\nint main(){}") == ["#include <windows.h>"])
check("fstream include is found",
      find_forbidden("#include <fstream>\nint main(){}") == ["#include <fstream>"])
check("clean cin/cout program has no forbidden items", find_forbidden(CLEAN) == [])
check("scanf is reported as a style warning",
      find_style_warnings('scanf("%d", &n);') == ["scanf"])
check("cin/cout program has no style warnings", find_style_warnings(CLEAN) == [])

print()
print("%d / %d checks passed" % (sum(results), len(results)))
if not all(results):
    raise SystemExit(1)