# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
# Import required libraries
import argparse
import os

# Import modules from the project
from tasks.execution_planner import build_execution_plan
from tasks.file_scanner import scan_and_classify
from tasks.file_mover import move_files
from tasks.report_generator import generate_report
from utils.logger import log_info, log_error
from utils.config_loader import get_config


# -------------------------------------------------
# TASK HANDLERS
# -------------------------------------------------
def handle_move(path, dry_run, folder_prefix):
    """
    Full file organization pipeline:

    1. Scan directory
    2. Classify files
    3. Build execution plan (DICT CONTRACT)
    4. Execute operations
    """

    log_info(f"move_start | dry_run={dry_run}")

    # -------------------------------------------------
    # STEP 1: SCAN
    # -------------------------------------------------
    classified_data = scan_and_classify(path)

    # -------------------------------------------------
    # SCAN VALIDATION
    # -------------------------------------------------
    # Scanner contract guarantees:
    # - dict on success
    # - None on failure
    if classified_data is None:

        log_error(
            f"scan_failed | "
            f"reason=scan_returned_none "
            f"path={path}"
        )

        return

    # -------------------------------------------------
    # STEP 2: BUILD PLAN (DICT CONTRACT)
    # -------------------------------------------------
    plan = build_execution_plan(
        path,
        classified_data,
        folder_prefix
    )

    # -------------------------------------------------
    # STRICT PLAN VALIDATION
    # -------------------------------------------------
    # Planner contract guarantees:
    # {
    #     "folders_to_create": [],
    #     "operations": [],
    #     "skipped": []
    # }
    if not isinstance(plan, dict):

        log_error(
            f"plan_failed | "
            f"reason=invalid_plan_type "
            f"received_type={type(plan).__name__}"
        )

        return

    # -------------------------------------------------
    # REQUIRED CONTRACT VALIDATION
    # -------------------------------------------------
    required_keys = [
        "operations",
        "folders_to_create",
        "skipped"
    ]

    for key in required_keys:

        if key not in plan:

            log_error(
                f"plan_failed | "
                f"reason=missing_plan_key "
                f"key={key}"
            )

            return

    # -------------------------------------------------
    # OPERATIONS VALIDATION
    # -------------------------------------------------
    operations = plan["operations"]

    if not isinstance(operations, list):

        log_error(
            f"plan_failed | "
            f"reason=invalid_operations_type "
            f"received_type={type(operations).__name__}"
        )

        return

    # -------------------------------------------------
    # PLAN SUMMARY
    # -------------------------------------------------
    log_info(
        f"plan_ready | "
        f"operations={len(operations)} "
        f"folders={len(plan['folders_to_create'])} "
        f"skipped={len(plan['skipped'])}"
    )

    # -------------------------------------------------
    # STEP 3: EXECUTE PLAN
    # -------------------------------------------------
    move_files(operations, dry_run)

    log_info("move_complete")


# -------------------------------------------------
# REPORT HANDLER
# -------------------------------------------------
def handle_report(path):
    """
    Executes reporting workflow.
    """

    log_info("report_start")

    generate_report(path)

    log_info("report_complete")


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main():
    """
    CLI entry point.

    Responsibilities:
    - Parse CLI arguments
    - Load configuration
    - Validate execution context
    - Route tasks
    """

    # -------------------------------------------------
    # CLI SETUP
    # -------------------------------------------------
    parser = argparse.ArgumentParser(
        description="Smart File Organizer CLI Tool"
    )

    parser.add_argument("task", type=str)
    parser.add_argument("path", type=str)

    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate filesystem changes"
    )

    args = parser.parse_args()

    # -------------------------------------------------
    # CONFIG
    # -------------------------------------------------
    config = get_config() or {}

    dry_run = args.dry_run or config.get(
        "dry_run",
        False
    )

    folder_prefix = config.get(
        "folder_prefix",
        "smartorg"
    )

    # -------------------------------------------------
    # STARTUP
    # -------------------------------------------------
    log_info("app_start | Smart File Organizer v0.7.0")

    # -------------------------------------------------
    # PATH VALIDATION
    # -------------------------------------------------
    if not os.path.exists(args.path):

        log_error(
            f"path_invalid | "
            f"reason=path_not_found "
            f"path={args.path}"
        )

        return

    # -------------------------------------------------
    # TASK RESOLUTION
    # -------------------------------------------------
    task = args.task.lower()

    log_info(
        f"context_task={task} | "
        f"path={args.path} | "
        f"dry_run={dry_run}"
    )

    # -------------------------------------------------
    # TASK ROUTING
    # -------------------------------------------------
    if task == "move":

        handle_move(
            args.path,
            dry_run,
            folder_prefix
        )

    elif task == "report":

        handle_report(args.path)

    else:

        log_error(
            f"task_unknown | "
            f"reason=unsupported_task "
            f"task={args.task}"
        )


# -------------------------------------------------
# ENTRY
# -------------------------------------------------
if __name__ == "__main__":
    main()