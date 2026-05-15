# -------------------------------------------------
# IMPORTS
# -------------------------------------------------

# Import required libraries
import argparse
import os

# Core project modules
from tasks.file_sorter import scan_and_classify
from tasks.file_mover import move_files
from tasks.report_generator import generate_report


# -------------------------------------------------
# TASK HANDLERS
# -------------------------------------------------

def handle_move(path):
    """
    Handles the full "move" workflow.

    Pipeline:
    1. Scan directory
    2. Classify files
    3. Move files into structured folders
    """

    # Step 1: Scan and classify directory contents
    classified_data = scan_and_classify(path)

    # Safety check in case scanning fails
    if classified_data is None:
        print("[ERROR] Failed to scan directory.")
        return

    # Debug output to inspect classification result
    print("\n[SCAN RESULT]")
    print(classified_data)

    # Step 2: Move files into categorized folders
    move_files(path, classified_data)


def handle_report(path):
    """
    Handles the "report" workflow.

    Currently a placeholder for future implementation.
    """
    generate_report(path)


# -------------------------------------------------
# MAIN APPLICATION ENTRY POINT
# -------------------------------------------------

def main():
    """
    Entry point of the Smart File Organizer CLI tool.

    Responsibilities:
    - Parse CLI arguments
    - Validate input
    - Route tasks to correct handlers
    """

    # -----------------------------
    # CLI ARGUMENT SETUP
    # -----------------------------
    parser = argparse.ArgumentParser(description="Smart File Organizer CLI Tool")

    # Task to execute (move, report)
    parser.add_argument(
        "task",
        type=str,
        help="Task to perform (move, report)"
    )

    # Target directory path
    parser.add_argument(
        "path",
        type=str,
        help="Path to the directory to process"
    )

    # Parse CLI input into usable variables
    args = parser.parse_args()

    # Debug output (useful during development)
    print(f"Received task: {args.task}")
    print(f"Received path: {args.path}")

    # -----------------------------
    # INPUT VALIDATION
    # -----------------------------

    # Ensure the provided path exists before proceeding
    if not os.path.exists(args.path):
        print("[ERROR] Path does not exist")
        return

    # -----------------------------
    # TASK ROUTING
    # -----------------------------

    # Route to move workflow
    if args.task == "move":
        handle_move(args.path)

    # Route to report workflow
    elif args.task == "report":
        handle_report(args.path)

    # Handle invalid task input
    else:
        print("[ERROR] Unknown task provided.")
        print("Available tasks: move, report")


# -------------------------------------------------
# ENTRY POINT GUARD
# -------------------------------------------------

if __name__ == "__main__":
    main()