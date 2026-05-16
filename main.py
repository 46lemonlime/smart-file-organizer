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
from utils.logger import log_info, log_error


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

    log_info("MOVE workflow started")

    # Step 1: Scan and classify directory contents
    classified_data = scan_and_classify(path)

    # Safety check in case scanning fails
    if classified_data is None:
        log_error(f"Scan failed for path: {path}")
        return

    # Step 2: Move files into categorized folders
    move_files(path, classified_data)

    log_info("MOVE workflow finished")


def handle_report(path):
    """
    Handles the "report" workflow.

    Currently a placeholder for future implementation.
    """
    
    log_info("REPORT workflow started")

    generate_report(path)

    log_info("REPORT workflow finished")


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
    parser.add_argument("task", type=str, help="Task to perform (move, report)")

    # Target directory path
    parser.add_argument("path", type=str, help="Path to the directory to process")

    # Parse CLI input into usable variables
    args = parser.parse_args()
    # -----------------------------
    # LOGGING: STARTUP (always safe)
    # -----------------------------
    log_info("Smart File Organizer started")

    # -----------------------------
    # INPUT VALIDATION (before context logging)
    # -----------------------------
    # Ensure the provided path exists before proceeding and logging the error if it doesn't
    if not os.path.exists(args.path):
        log_error(f"Path does not exist: {args.path}")
        return

    # -----------------------------
    # LOGGING: CONFIRMED EXECUTION CONTEXT
    # -----------------------------
    log_info(f"Executing task: {args.task}")
    log_info(f"Target path: {args.path}")

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
        log_error(f"Unknown task provided: {args.task}")


# -------------------------------------------------
# ENTRY POINT GUARD
# -------------------------------------------------

if __name__ == "__main__":
    main()