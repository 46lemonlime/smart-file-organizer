#Phase 1: SKELETON (No real logic yet)
#Goal: CanI run the program end to end without errors?
'''
1. main.py
- CLI input works (task, path)
- prints received argumetns
- routes to a placeholder function for the task
+ no file moving yet
+ no config yet
+ no reports yet
'''
#Phase 2: 
#Goal: “Can I see what exists in a folder?”
'''
2. tasks/file_sorter.py
- Scan directory
- Return list of files
- Print or log them
'''
#import necessary libraries
import argparse

#import placeholder functions for future logic
from tasks.file_sorter import move_files
from tasks.report_generator import generate_report

def main():
    # Set up argument parser
    parser = argparse.ArgumentParser(description="File management tool")

    parser.add_argument(
        "task",
        type=str,
        help="Task to perform (e.g., move, report)"
    )

    parser.add_argument(
        "path",
        type=str,
        help="Path to the directory or file"
    )

    # Parse arguments
    args = parser.parse_args()

    # Print received arguments (debug visibility)
    print(f"Received task: {args.task}")
    print(f"Received path: {args.path}")

    # Route to placeholder functions based on task
    if args.task == "move":
        move_files(args.path)

    elif args.task == "report":
        generate_report(args.path)

    else:
        print("[ERROR] Unknown task.")
        print("Available tasks: move, report")


if __name__ == "__main__":
    main()