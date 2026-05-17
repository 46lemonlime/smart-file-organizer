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
from utils.config_loader import get_config


# -------------------------------------------------
# TASK HANDLERS
# -------------------------------------------------
def handle_move(path, dry_run):
    """
    Executes full file organization pipeline.

    Pipeline:
    1. Scan directory
    2. Classify files
    3. Move files into structured folders
    """

    log_info(f"move_start | dry_run={dry_run}")

    # Step 1: Scan and classify directory contents
    classified_data = scan_and_classify(path)

    # Safety check in case scanning fails
    if classified_data is None:
        log_error(f"scan_failed | path={path}")
        return

    # Step 2: Execute file movement phase
    # Execution mode is propagated from main to ensure consistency
    move_files(path, classified_data, dry_run)

    log_info("move_complete")


def handle_report(path):
    """
    Handles report generation workflow.

    Currently a placeholder for future implementation.
    """

    log_info("report_start")

    generate_report(path)

    log_info("report_complete")


# -------------------------------------------------
# MAIN APPLICATION ENTRY POINT
# -------------------------------------------------
def main():
    """
    CLI entry point for Smart File Organizer.

    Responsibilities:
    - Parse arguments
    - Resolve execution mode
    - Route tasks
    """

    # -----------------------------
    # CLI ARGUMENT SETUP
    # -----------------------------
    parser = argparse.ArgumentParser(description="Smart File Organizer CLI Tool")

    parser.add_argument("task", type=str, help="Task to perform (move, report)")
    parser.add_argument("path", type=str, help="Path to directory to process")

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate actions without modifying filesystem"
    )

    args = parser.parse_args()

    # -----------------------------
    # LOAD CONFIGURATION
    # -----------------------------
    config = get_config() or {}

    # -----------------------------
    # RESOLVE EXECUTION MODE
    # -----------------------------
    # Execution priority (highest → lowest):
    # 1. CLI argument (--dry-run)
    # 2. config.yaml setting
    #
    # This ensures runtime behavior can always be overridden
    # without modifying persistent configuration files.
    dry_run = args.dry_run or config.get("dry_run", False)

    # -----------------------------
    # STARTUP LOG
    # -----------------------------
    log_info("app_start | Smart File Organizer v0.6.0")

    # -----------------------------
    # INPUT VALIDATION
    # -----------------------------
    if not os.path.exists(args.path):
        log_error(f"path_invalid | path={args.path}")
        return

    task = args.task.lower()

    # -----------------------------
    # EXECUTION CONTEXT LOG
    # -----------------------------
    log_info(f"context_task={task} | path={args.path} | dry_run={dry_run}")

    # -----------------------------
    # TASK ROUTING
    # -----------------------------
    if task == "move":
        handle_move(args.path, dry_run)

    elif task == "report":
        handle_report(args.path)

    else:
        log_error(f"task_unknown | task={args.task}")


# -------------------------------------------------
# ENTRY POINT GUARD
# -------------------------------------------------
if __name__ == "__main__":
    main()