import os
import sys
import subprocess

def main():
    if len(sys.argv) != 3:
        print("Usage: python batch_judge.py <submissions_folder> <testcase_file>")
        sys.exit(1)

    submissions_dir = sys.argv[1]
    testcase_file = sys.argv[2]

    if not os.path.isdir(submissions_dir):
        print(f"Error: Directory not found: {submissions_dir}")
        sys.exit(1)

    if not os.path.isfile(testcase_file):
        print(f"Error: Testcase file not found: {testcase_file}")
        sys.exit(1)

    cpp_files = [f for f in os.listdir(submissions_dir) if f.endswith('.cpp')]
    if not cpp_files:
        print(f"No .cpp files found in {submissions_dir}")
        sys.exit(0)

    print(f"Found {len(cpp_files)} submissions. Starting batch run...\n")
    
    log_file = "batch_summary.txt"
    with open(log_file, "w", encoding="utf-8") as log:
        log.write(f"Batch Run Summary\nSubmissions: {submissions_dir}\nTestcases: {testcase_file}\n")
        log.write("="*50 + "\n\n")

    success_count = 0
    review_count = 0

    for i, filename in enumerate(cpp_files, 1):
        filepath = os.path.join(submissions_dir, filename)
        print(f"--- [{i}/{len(cpp_files)}] Judging {filename} ---")
        
        # Run judge.py
        cmd = [sys.executable, "judge.py", filepath, testcase_file]
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print output to console
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
            
        # Log to summary file
        with open(log_file, "a", encoding="utf-8") as log:
            log.write(f"File: {filename}\n")
            if result.returncode == 0:
                log.write("Status: SUCCESS\n")
                success_count += 1
                # Extract TOTAL SCORE line
                for line in result.stdout.splitlines():
                    if "TOTAL SCORE" in line:
                        log.write(f"{line}\n")
            elif result.returncode == 2:
                log.write("Status: NEEDS MANUAL REVIEW\n")
                review_count += 1
            elif result.returncode == 1:
                print(f"\nFATAL ERROR: judge.py exited with code 1 on {filename}.")
                print("Stopping batch process. Check the error above.")
                log.write("Status: FATAL ERROR (Batch stopped)\n")
                sys.exit(1)
            else:
                log.write(f"Status: UNKNOWN ERROR (Code {result.returncode})\n")
            
            log.write("-" * 30 + "\n")
        
        print(f"Finished {filename}. Exit code: {result.returncode}\n")

    print("="*50)
    print(f"Batch complete! {success_count} judged, {review_count} need manual review.")
    print(f"Summary saved to {log_file}")

if __name__ == "__main__":
    main()