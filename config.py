# config.py - all judge settings in one place
import os

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

SUBMISSIONS_DIR = os.path.join(BASE_DIR, "Subtests")
TESTS_DIR = os.path.join(BASE_DIR, "Testcases")
WORK_DIR = os.path.join(BASE_DIR, "work")
RESULTS_DIR = os.path.join(BASE_DIR, "results")

COMPILER = "g++"
COMPILER_FLAGS = ["-std=c++17", "-O2"]

COMPILE_TIMEOUT_SEC = 30
RUN_TIMEOUT_SEC = 2
MAX_OUTPUT_BYTES = 1000000  # the program is killed as soon as it prints more

# testcase format (judge_formats.md, section 2)
BASE_CASE_COUNT = 6
EDGE_CASE_COUNT = 2
BASE_POINTS = 1
EDGE_POINTS = 2

# manual review: compare the ID in the filename (Name_ID.cpp) with the header ID
CHECK_FILENAME_ID = True