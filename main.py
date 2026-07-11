# -------------------------------------------------
# SMART FILE ORGANIZER - APPLICATION ENTRY POINT
# -------------------------------------------------
"""
This module serves as the application entry point and
top-level orchestration layer.

Responsibilities:
- Consume parsed CLI arguments
- Load application configuration
- Validate execution context
- Route supported tasks
- Coordinate high-level application flow
- Inject runtime dependencies into subsystems
- Route report history actions and references
- Route individual and scoped report deletion requests
- Route application log cleanup requests

Architecture Role:
This file intentionally contains NO logic related to:
- CLI parser construction
- filesystem discovery
- file filtering
- file classification
- execution planning
- filesystem mutations
- rollback implementation
- report persistence implementation
- report reconstruction implementation
- report rendering implementation
- report history construction
- report deletion implementation
- log cleanup implementation

Instead, it functions as the composition root responsible
for wiring together the application's subsystems.

CLI parsing is delegated to cli/parser.py.

Application Flow:
CLI parsing
→ configuration loading
→ dependency injection
→ execution context validation
→ task routing
→ subsystem execution

Subsystems:
- cli:
    Command-line parsing and argument validation
- discovery:
    Filesystem discovery and classification
- execution:
    Planning and filesystem mutations
- rollback:
    Rollback workflow coordination
- reporting:
    Report generation, persistence, loading, history,
    cleanup, and presentation

Design Principles:
- minimal orchestration
- separation of concerns
- contract-first architecture
- deterministic application flow
- centralized dependency composition
- explicit dependency injection

Failure Contract:
- validates execution context before routing
- prevents invalid task execution
- handles unavailable persisted reports safely
- handles unavailable application logs safely
- provides actionable CLI feedback
- delegates subsystem failures to their owners

Observability:
Structured logs are emitted throughout execution to provide:
- application lifecycle visibility
- execution context diagnostics
- task routing traceability
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
# Import modules from the project
from tasks.execution.planner import build_execution_plan
from tasks.discovery.coordinator import discover_files
from tasks.execution.mover import move_files

from tasks.reporting.cleaner import (
    clear_application_logs,
    delete_report_by_reference,
    delete_reports_by_scope
)

from tasks.reporting.loader import (
    list_report_history,
    load_latest_execution_report,
    load_report_by_reference
)

from tasks.reporting.reporter import (
    render_deleted_report,
    render_deleted_reports,
    render_execution_report,
    render_report_history,
    render_rollback_report
)

from tasks.rollback.coordinator import rollback_latest_execution

from cli.parser import parse_args

from tasks.reporting.generator import (
    build_discovery_report,
    build_planning_report,
    build_execution_report
)

from tasks.reporting.saver import save_report

from utils.logger import log_info, log_error
from utils.config_loader import get_config

from core.contracts import (
    ExecutionReport,
    RollbackReport
)

from core.metadata import (
    APP_BANNER
)

from core.events import (
    APP_START,
    EXECUTION_CONTEXT,
    REPORT_SKIPPED,
    DISCOVERY_FAILED,
    PLAN_READY,
    MOVE_START,
    MOVE_COMPLETE,
    REPORT_START,
    REPORT_COMPLETE
)


# -------------------------------------------------
# APPLICATION PERSISTENCE PATHS
# -------------------------------------------------
LOGS_DIRECTORY = "logs"
LOG_FILENAME = "smartorg.log"


# -------------------------------------------------
# TASK HANDLERS
# -------------------------------------------------
def handle_move(
    path: str,
    dry_run: bool,
    folder_prefix: str,
    reports_directory: str,
    execution_reports_directory: str
) -> None:
    """
    Executes the full organization pipeline.

    IMPORTANT:
    Reporting persistence configuration is injected by
    the application composition root.

    This handler coordinates report generation while
    delegating persistence and presentation to the
    reporting subsystem.
    """

    log_info(
        f"{MOVE_START} | "
        f"dry_run={dry_run}"
    )

    # -------------------------------------------------
    # STEP 1: DISCOVERY
    # -------------------------------------------------
    discovery_result = discover_files(path)

    # -------------------------------------------------
    # DISCOVERY VALIDATION
    # -------------------------------------------------
    if discovery_result is None:

        log_error(
            f"{DISCOVERY_FAILED} | "
            f"reason=discovery_returned_none "
            f"path={path}"
        )

        return

    classified_data = discovery_result.classified_data

    # -------------------------------------------------
    # STEP 2: BUILD EXECUTION PLAN
    # -------------------------------------------------
    plan = build_execution_plan(
        path,
        classified_data,
        folder_prefix
    )

    # -------------------------------------------------
    # PLAN SUMMARY
    # -------------------------------------------------
    log_info(
        f"{PLAN_READY} | "
        f"operations={len(plan.operations)} "
        f"folders={len(plan.folders_to_create)} "
        f"skipped={len(plan.skipped)}"
    )

    # -------------------------------------------------
    # STEP 3: EXECUTE PLAN
    # -------------------------------------------------
    mover_report = move_files(
        plan.operations,
        dry_run
    )

    # -------------------------------------------------
    # STEP 4: GENERATE EXECUTION REPORT
    # -------------------------------------------------
    discovery_report = build_discovery_report(
        path,
        classified_data,
        skipped_items=discovery_result.skipped_items
    )

    planning_report = build_planning_report(
        plan
    )

    execution_report = build_execution_report(
        path,
        discovery_report,
        planning_report,
        mover_report
    )

    # -------------------------------------------------
    # STEP 5: SAVE EXECUTION REPORT
    # -------------------------------------------------
    save_report(
        execution_report,
        reports_directory,
        execution_reports_directory
    )

    # -------------------------------------------------
    # STEP 6: RENDER EXECUTION REPORT
    # -------------------------------------------------
    render_execution_report(
        execution_report
    )

    log_info(
        f"{MOVE_COMPLETE} | "
        f"dry_run={execution_report.mover.dry_run} "
        f"processed={execution_report.mover.total_processed} "
        f"failed={execution_report.mover.total_failed}"
    )


# -------------------------------------------------
# REPORT HANDLER
# -------------------------------------------------
def handle_report(
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str,
    logs_directory: str,
    log_filename: str,
    action: str | None,
    reference: str | None
) -> None:
    """
    Executes the reporting presentation and cleanup workflow.

    Supported actions:
    - no action:
        load and render the latest execution report
    - list:
        render unified chronological report history
    - numeric index:
        load and render the selected history report
    - report identifier:
        load and render the matching persisted report
    - clear <index>:
        delete one report by history index
    - clear <identifier>:
        delete one report by report identifier
    - clear executions:
        delete all persisted execution reports
    - clear rollbacks:
        delete all persisted rollback reports
    - clear all:
        delete all persisted reports
    - clear logs:
        clear the persisted application log file

    IMPORTANT:
    This handler only routes reporting and cleanup workflows.
    Report loading, reconstruction, history construction,
    reference resolution, deletion, log cleanup, and rendering
    remain delegated to their owning subsystems.
    """

    log_info(
        f"{REPORT_START} | "
        f"action={action or 'latest'} "
        f"reference={reference}"
    )

    # -------------------------------------------------
    # REPORT HISTORY
    # -------------------------------------------------
    if action == "list":

        history_items = list_report_history(
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory
        )

        if not history_items:

            print()
            print("Reports")
            print("-------")
            print()
            print("No reports found.")
            print()

            log_info(
                f"{REPORT_SKIPPED} | "
                "reason=no_persisted_reports "
                "action=list"
            )

            return

        render_report_history(
            history_items
        )

        log_info(
            f"{REPORT_COMPLETE} | "
            f"action=list "
            f"reports={len(history_items)}"
        )

        return

    # -------------------------------------------------
    # PERSISTENCE CLEANUP
    # -------------------------------------------------
    if action == "clear":

        # -------------------------------------------------
        # MISSING CLEANUP REFERENCE
        # -------------------------------------------------
        if reference is None:

            print()
            print("Missing report index, identifier, or scope.")
            print()
            print("Use:")
            print()
            print(
                "    python3 main.py report clear "
                "<index_or_identifier>"
            )
            print(
                "    python3 main.py report clear "
                "executions"
            )
            print(
                "    python3 main.py report clear "
                "rollbacks"
            )
            print(
                "    python3 main.py report clear "
                "all"
            )
            print(
                "    python3 main.py report clear "
                "logs"
            )
            print()
            print("Available reports can be viewed with:")
            print()
            print("    python3 main.py report list")
            print()

            log_info(
                f"{REPORT_SKIPPED} | "
                "reason=missing_cleanup_reference "
                "action=clear"
            )

            return

        # -------------------------------------------------
        # APPLICATION LOG CLEANUP
        # -------------------------------------------------
        if reference == "logs":

            logs_cleared = clear_application_logs(
                logs_directory,
                log_filename
            )

            if not logs_cleared:

                print()
                print("Logs not found.")
                print(
                    "No persisted application log file "
                    "is available."
                )
                print()

                log_info(
                    f"{REPORT_SKIPPED} | "
                    "reason=log_file_not_found "
                    "action=clear "
                    "scope=logs"
                )

                return

            print()
            print("Cleared Logs")
            print("------------")
            print()
            print(
                f"File: {logs_directory}/{log_filename}"
            )
            print()

            log_info(
                f"{REPORT_COMPLETE} | "
                "action=clear "
                "scope=logs"
            )

            return

        deletion_scopes = {
            "executions",
            "rollbacks",
            "all"
        }

        # -------------------------------------------------
        # SCOPED REPORT DELETION
        # -------------------------------------------------
        if reference in deletion_scopes:

            deleted_items = delete_reports_by_scope(
                reference,
                reports_directory,
                execution_reports_directory,
                rollback_reports_directory
            )

            if not deleted_items:

                print()
                print("No reports deleted.")
                print(
                    f"No persisted reports matched "
                    f"the '{reference}' scope."
                )
                print()

                log_info(
                    f"{REPORT_SKIPPED} | "
                    f"reason=no_matching_reports "
                    f"action=clear "
                    f"scope={reference}"
                )

                return

            render_deleted_reports(
                deleted_items,
                reference
            )

            log_info(
                f"{REPORT_COMPLETE} | "
                f"action=clear "
                f"scope={reference} "
                f"deleted={len(deleted_items)}"
            )

            return

        # -------------------------------------------------
        # INDIVIDUAL REPORT DELETION
        # -------------------------------------------------
        deleted_item = delete_report_by_reference(
            reference,
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory
        )

        if deleted_item is None:

            print()
            print("Report not found.")
            print("Invalid report index or identifier.")
            print()
            print("Use:")
            print()
            print("    python3 main.py report list")
            print()
            print("to view available reports.")
            print()

            log_info(
                f"{REPORT_SKIPPED} | "
                f"reason=report_delete_not_found "
                f"reference={reference}"
            )

            return

        render_deleted_report(
            deleted_item
        )

        log_info(
            f"{REPORT_COMPLETE} | "
            f"action=clear "
            f"report_id={deleted_item.report_id} "
            f"report_type={deleted_item.report_type}"
        )

        return

    # -------------------------------------------------
    # UNEXPECTED SECOND ARGUMENT
    # -------------------------------------------------
    if reference is not None:

        print()
        print("Invalid report command.")
        print()
        print("Use:")
        print()
        print("    python3 main.py report")
        print("    python3 main.py report list")
        print("    python3 main.py report <index_or_identifier>")
        print(
            "    python3 main.py report clear "
            "<index_or_identifier>"
        )
        print("    python3 main.py report clear executions")
        print("    python3 main.py report clear rollbacks")
        print("    python3 main.py report clear all")
        print("    python3 main.py report clear logs")
        print()

        log_info(
            f"{REPORT_SKIPPED} | "
            f"reason=unexpected_report_reference "
            f"action={action} "
            f"reference={reference}"
        )

        return

    # -------------------------------------------------
    # LATEST EXECUTION REPORT
    # -------------------------------------------------
    if action is None:

        report = load_latest_execution_report(
            reports_directory,
            execution_reports_directory
        )

        report_reference = "latest"

    # -------------------------------------------------
    # REPORT BY INDEX OR IDENTIFIER
    # -------------------------------------------------
    else:

        report = load_report_by_reference(
            action,
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory
        )

        report_reference = action

    # -------------------------------------------------
    # REPORT AVAILABILITY VALIDATION
    # -------------------------------------------------
    if report is None:

        log_info(
            f"{REPORT_SKIPPED} | "
            f"reason=report_not_found "
            f"reference={report_reference}"
        )

        if action is not None:

            print()
            print("Report not found.")
            print("Invalid report index or identifier.")
            print()
            print("Use:")
            print()
            print("    python3 main.py report list")
            print()
            print("to view available reports.")
            print()

        else:

            print()
            print("Report not found.")
            print("No persisted execution reports are available.")
            print()

        return

    # -------------------------------------------------
    # REPORT TYPE ROUTING
    # -------------------------------------------------
    if isinstance(
        report,
        ExecutionReport
    ):

        render_execution_report(
            report
        )

        report_type = "execution"

    elif isinstance(
        report,
        RollbackReport
    ):

        render_rollback_report(
            report
        )

        report_type = "rollback"

    else:

        log_error(
            f"{REPORT_SKIPPED} | "
            "reason=unsupported_report_contract "
            f"type={type(report).__name__}"
        )

        return

    log_info(
        f"{REPORT_COMPLETE} | "
        f"type={report_type} "
        f"reference={report_reference}"
    )


# -------------------------------------------------
# ROLLBACK HANDLER
# -------------------------------------------------
def handle_rollback(
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str,
    dry_run: bool
) -> None:
    """
    Executes rollback workflow for the latest execution report.

    IMPORTANT:
    Rollback execution is delegated to the rollback subsystem.
    This handler only injects runtime dependencies and routes
    the workflow from the composition root.
    """

    rollback_report = rollback_latest_execution(
        reports_directory,
        execution_reports_directory,
        dry_run
    )

    if rollback_report is None:

        return

    save_report(
        rollback_report,
        reports_directory,
        rollback_reports_directory
    )

    render_rollback_report(
        rollback_report
    )

    log_info(
        f"rollback_complete | "
        f"dry_run={rollback_report.dry_run} "
        f"processed={rollback_report.total_processed} "
        f"failed={rollback_report.total_failed}"
    )


# -------------------------------------------------
# MAIN
# -------------------------------------------------
def main() -> None:
    """
    CLI entry point.
    """

    args = parse_args()

    # -------------------------------------------------
    # CONFIG
    # -------------------------------------------------
    config = get_config()

    dry_run = getattr(
        args,
        "dry_run",
        False
    ) or config.dry_run

    folder_prefix = config.folder_prefix

    reports_directory = config.reports_directory

    execution_reports_directory = (
        config.execution_reports_directory
    )

    rollback_reports_directory = (
        config.rollback_reports_directory
    )

    # -------------------------------------------------
    # STARTUP
    # -------------------------------------------------
    log_info(
        f"{APP_START} | "
        f"banner={APP_BANNER}"
    )

    # -------------------------------------------------
    # EXECUTION CONTEXT
    # -------------------------------------------------
    task = args.task

    path = getattr(
        args,
        "path",
        None
    )

    report_action = getattr(
        args,
        "action",
        None
    )

    report_reference = getattr(
        args,
        "reference",
        None
    )

    log_info(
        f"{EXECUTION_CONTEXT} | "
        f"task={task} "
        f"path={path} "
        f"report_action={report_action} "
        f"report_reference={report_reference} "
        f"dry_run={dry_run}"
    )

    # -------------------------------------------------
    # TASK ROUTING
    # -------------------------------------------------
    if task == "move":

        handle_move(
            path,
            dry_run,
            folder_prefix,
            reports_directory,
            execution_reports_directory
        )

    elif task == "report":

        handle_report(
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory,
            LOGS_DIRECTORY,
            LOG_FILENAME,
            report_action,
            report_reference
        )

    elif task == "rollback":

        handle_rollback(
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory,
            dry_run
        )


# -------------------------------------------------
# ENTRY
# -------------------------------------------------
if __name__ == "__main__":
    main()