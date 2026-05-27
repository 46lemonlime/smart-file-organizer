"""
Smart File Organizer - Main Application Entry Point

This module acts as the orchestration layer of the application.

Responsibilities:
- Parse CLI arguments
- Load and propagate runtime configuration
- Validate execution context
- Route supported tasks
- Coordinate high-level pipeline execution
- Enforce inter-module contract validation
- Provide top-level execution observability

Architecture Role:
This file intentionally contains NO business logic related to:
- filesystem discovery
- file filtering
- classification
- execution planning
- filesystem mutations

Instead, it functions as the top-level orchestration layer
responsible for coordinating execution flow between
specialized pipeline modules.

Pipeline Overview:
CLI
→ configuration loading
→ context validation
→ discovery coordination
→ execution planning
→ filesystem execution

Supported Tasks:
- move:
    Full organization pipeline execution
- report:
    Reporting workflow entrypoint (future expansion)

Design Principles:
- separation of concerns
- deterministic orchestration
- explicit contract validation
- config-driven execution
- structured observability
- failure isolation

Contract Enforcement:
This module validates downstream module contracts before
continuing execution to prevent cascading failures and
improve debugging clarity.

Observability:
Structured logs are emitted throughout execution to provide:
- execution traceability
- operational visibility
- pipeline diagnostics
- failure localization
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
# Import required libraries
import argparse
import os

# Import modules from the project
from tasks.execution.planner import build_execution_plan
from tasks.discovery.coordinator import discover_files
from tasks.execution.executor import move_files
from tasks.reporting.reporter import generate_report

from utils.logger import log_info, log_error
from utils.config_loader import get_config

# Import shared contracts
from contracts import ExecutionPlan


# -------------------------------------------------
# TASK HANDLERS
# -------------------------------------------------
def handle_move(
    path: str,
    dry_run: bool,
    folder_prefix: str
):
    """
    Executes the full organization pipeline.

    PIPELINE:
    1. Discover filesystem entities
    2. Classify discovered files
    3. Build deterministic execution plan
    4. Execute filesystem operations
    """

    log_info(f"move_start | dry_run={dry_run}")

    # -------------------------------------------------
    # STEP 1: DISCOVERY
    # -------------------------------------------------
    classified_data = discover_files(path)

    # -------------------------------------------------
    # DISCOVERY VALIDATION
    # -------------------------------------------------
    # Coordinator contract guarantees:
    # - dict on success
    # - None on failure
    if classified_data is None:

        log_error(
            f"discovery_failed | "
            f"reason=discovery_returned_none "
            f"path={path}"
        )

        return

    # -------------------------------------------------
    # STEP 2: BUILD EXECUTION PLAN
    # -------------------------------------------------
    plan = build_execution_plan(
        path,
        classified_data,
        folder_prefix
    )

    # -------------------------------------------------
    # PLAN CONTRACT VALIDATION
    # -------------------------------------------------
    # Planner contract guarantees:
    # - ExecutionPlan object
    if not isinstance(plan, ExecutionPlan):

        log_error(
            f"plan_failed | "
            f"reason=invalid_plan_contract "
            f"received_type={type(plan).__name__}"
        )

        return

    # -------------------------------------------------
    # PLAN SUMMARY
    # -------------------------------------------------
    log_info(
        f"plan_ready | "
        f"operations={len(plan.operations)} "
        f"folders={len(plan.folders_to_create)} "
        f"skipped={len(plan.skipped)}"
    )

    # -------------------------------------------------
    # STEP 3: EXECUTE PLAN
    # -------------------------------------------------
    move_files(
        plan.operations,
        dry_run
    )

    log_info("move_complete")


# -------------------------------------------------
# REPORT HANDLER
# -------------------------------------------------
def handle_report(path: str):
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
    log_info(
        "app_start | "
        "Smart File Organizer v0.7.0"
    )

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