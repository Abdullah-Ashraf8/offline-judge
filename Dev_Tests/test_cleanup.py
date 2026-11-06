# test_cleanup.py - automated checks for cleanup.py
import os
import tempfile

import cleanup
import config

results = []


def check(label, condition):
    print(("PASS  " if condition else "FAIL  ") + label)
    results.append(bool(condition))


def touch(path):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write("x\n")


with tempfile.TemporaryDirectory() as root:
    build = os.path.join(root, "bob_1002")
    touch(os.path.join(build, "p1.cpp"))
    cleanup.remove_build_dir(build)
    check("remove_build_dir deletes the folder", not os.path.exists(build))
    cleanup.remove_build_dir(build)
    check("remove_build_dir tolerates a missing folder", True)

    work = os.path.join(root, "work")
    saved_work = config.WORK_DIR
    try:
        config.WORK_DIR = work
        os.makedirs(work)
        cleanup.remove_empty_work_dir()
        check("remove_empty_work_dir removes an empty work folder",
              not os.path.exists(work))

        os.makedirs(work)
        touch(os.path.join(work, "kept.txt"))
        cleanup.remove_empty_work_dir()
        check("remove_empty_work_dir keeps a non-empty work folder",
              os.path.isfile(os.path.join(work, "kept.txt")))
    finally:
        config.WORK_DIR = saved_work

    project = os.path.join(root, "project")
    touch(os.path.join(project, "__pycache__", "a.pyc"))
    touch(os.path.join(project, "pkg", "__pycache__", "b.pyc"))
    touch(os.path.join(project, "pkg", "keep.py"))
    saved_base = config.BASE_DIR
    try:
        config.BASE_DIR = project
        cleanup.remove_pycache()
        check("remove_pycache deletes nested cache folders",
              not os.path.exists(os.path.join(project, "__pycache__"))
              and not os.path.exists(os.path.join(project, "pkg", "__pycache__")))
        check("remove_pycache keeps normal files",
              os.path.isfile(os.path.join(project, "pkg", "keep.py")))
    finally:
        config.BASE_DIR = saved_base

print()
print("%d / %d checks passed" % (sum(results), len(results)))
if not all(results):
    raise SystemExit(1)
