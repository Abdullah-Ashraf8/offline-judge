# Offline Judge: User Guide and Program Flow

Welcome to the Offline C++ Judge! This tool is built to automatically grade student submissions for the **C++ & Problem Solving Bootcamp (Level 0)**. 

This guide explains how to use the program, what you need to run it, and exactly how it processes a student's file step by step.

---

## 1. What You Need to Run It

Before you start, make sure the Windows computer you are using has the following installed:
*   **Python 3:** To run the judge script.
*   **g++ Compiler (MinGW):** This comes with Code::Blocks. Make sure the MinGW `bin` folder is added to your Windows PATH so that you can run `g++` directly from the command prompt.

---

## 2. How to Run the Program

The judge is designed to evaluate **one student file at a time**. Open your command prompt (cmd), go to the project folder (`E:\judge`), and run this command:

```cmd
python judge.py <path_to_student_file.cpp> <path_to_testcase_file.txt>
```

**Example:**
```cmd
python judge.py submissions\demo\bob_1002.cpp tests\demo.txt
```

---

## 3. How the Program Works (Step-by-Step Flow)

Once you press enter, the program goes through the following steps automatically:

### Step 1: Check the Input
The program checks if you provided exactly two files (the student's `.cpp` file and the testcase `.txt` file). If a file is missing, it will stop and tell you.

### Step 2: Read the Testcases
It reads the text file containing the expected inputs and outputs. It checks that every problem has exactly 8 cases (6 base cases, 2 edge cases) and that there are no formatting mistakes. 

### Step 3: Read the Student's Code
The program scans the student's `.cpp` file to extract two main things:
1.  **The Identification Header:** It looks at line 1 to get the student's Name, Email, and ID.
2.  **The Answers:** It searches for blocks of code wrapped inside comments like `/* Problem 1 ... */`. Each block is treated as a completely separate program.

### Step 4: The "Manual Review" Check
Before grading, the judge does a strict check on the student's file format. It will **stop grading and ask for a manual review** (exit code 2) if:
*   The first line is not the correct identification comment.
*   The student left the header blank (e.g., leaving "[your ID]" instead of typing their actual ID).
*   The Student ID inside the file does not match the Student ID in the file's name.

### Step 5: Compile and Run (The Grading)
For each problem found in the testcase file, the judge will:
1.  Create a temporary folder (inside `work\`).
2.  Save the student's answer for that problem as a standalone `.cpp` file.
3.  **Compile it** using C++17 rules (allowing up to 30 seconds).
4.  **Run it** against all 8 test cases. The student's code has a strict limit of 2 seconds to solve each case.

### Step 6: Print the Report
Finally, the judge prints a clean report directly to your console. It will list the student's name, any warnings (like empty problem blocks), the pass/fail status of every single test case, and the **Total Score** at the bottom.

---

## 4. Understanding the Results (Verdicts)

When the report is printed, you will see a verdict for every testcase. Here is what they mean:

*   **[AC] Accepted:** The student's output perfectly matches the expected output (ignoring extra spaces at the end of lines). *Points awarded!*
*   **[WA] Wrong Answer:** The student's code finished running, but the printed answer was incorrect.
*   **[TLE] Time Limit Exceeded:** The code took longer than 2 seconds (usually means an infinite loop).
*   **[CE] Compile Error:** The code had syntax errors and could not be built. All cases for this problem will fail.
*   **[RE] Runtime Error:** The program crashed or returned an exit code other than 0.
*   **[OLE] Output Limit Exceeded:** The program printed too much text (over 1,000,000 characters).
*   **MISSING:** The student forgot to include the `/* Problem N */` block for this specific question.

---

## 5. Important Notes for Reviewers

*   **No CSV Output:** This judge simply prints the results to the screen. You will need to manually record the total score in the `Leaderboard.xlsx` file.
*   **Cleanliness/Bonus points:** The judge only grades functionality. You still need to manually add points for clean code, original logic, or specific bonus tricks as per the course policy.