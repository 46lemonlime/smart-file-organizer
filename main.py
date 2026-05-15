# Import required libraries
import argparse

# Import the core logic from tasks module
from tasks.file_sorter import scan_and_classify
from tasks.report_generator import generate_report

def main():
    """
    Entry point of the Smart File Organizer CLI tool.

    Responsibilities:
    - Parse command line arguments
    - Route task to the correct module
    - Display results
    """

    # -----------------------------
    # 1. Set up CLI argument parser
    # -----------------------------
    parser = argparse.ArgumentParser(description="Smart File Organizer CLI Tool")

    # Task to perform (e.g. move, report)
    parser.add_argument(
        "task",
        type=str,
        help="Task to perform (currently supported: move, report)"
    )

    # Path to target directory
    parser.add_argument(
        "path",
        type=str,
        help="Path to the directory to process"
    )

    # -----------------------------
    # 2. Parse arguments from CLI
    # -----------------------------
    args = parser.parse_args()

    # Debug output to confirm input values
    print(f"Received task: {args.task}")
    print(f"Received path: {args.path}")

    # -----------------------------
    # 3. Route tasks
    # -----------------------------

    # Phase 3.5: scan + classify files
    if args.task == "move":
        result = scan_and_classify(args.path)

        # Display structured output
        print("\nResult:")
        print(result)

    # Placeholder for future feature
    elif args.task == "report":
        generate_report(args.path)

    # Handle invalid task input
    else:
        print("[ERROR] Unknown task provided.")
        print("Available tasks: move, report")


# -----------------------------
# 4. Entry point guard
# -----------------------------
if __name__ == "__main__":
    main()