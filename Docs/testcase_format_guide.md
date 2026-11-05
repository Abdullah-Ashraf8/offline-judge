# Testcase Format Guide

This document explains exactly how to format the testcase text files (e.g., `tests/demo.txt`) so the Offline Judge can read them correctly. 

Anyone writing test cases for the bootcamp assignments (like Youssef) should follow this format strictly.

## 1. Rules for Writing Test Cases

* **Problem Headers:** Each problem must start with the word `Problem` followed by the number (e.g., `Problem 1`) on its own line.
* **Cases per Problem:** Every problem **must** have exactly 8 test cases.
  * Cases 1 to 6 are base cases (worth 1 point each). They start with `Case N:`.
  * Cases 7 and 8 are edge cases (worth 2 points each). They **must** be labeled as `Case N (Edge):`.
* **Input and Output Labels:** Every single case must contain an `Input:` line followed by the input data, and an `Output:` line followed by the expected output.
* **Formatting constraints:** 
  * The judge ignores trailing spaces at the end of a line and blank lines at the very end of the output. Everything else must match exactly.
  * *Important:* Do not use the exact words `Problem 1`, `Case 1:`, `Input:`, or `Output:` inside the actual input or expected output data, as the program will mistake them for section labels.

## 2. Example Testcase File

Here is a template/example showing how to write the test cases for a single problem:

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

To add the next problem, simply drop down to a new line and write `Problem 2`, followed by its 8 cases in the exact same structure.