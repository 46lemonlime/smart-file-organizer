# -------------------------------------------------
# SMART FILE ORGANIZER - APPLICATION HANDLERS
# -------------------------------------------------
"""
This module defines the application's high-level task handlers.

Responsibilities:
- Coordinate move workflows
- Coordinate rollback workflows
- Coordinate report presentation workflows
- Coordinate report history workflows
- Coordinate report and log cleanup workflows
- Connect specialized subsystems
- Provide user-facing CLI feedback

Architecture Role:
This module acts as the application orchestration layer
between the CLI composition root and specialized subsystems.

It intentionally contains NO logic related to:
- CLI parser construction
- configuration loading
- raw filesystem discovery
- file filtering
- file classification
- execution planning implementation
- filesystem mutation implementation
- rollback planning implementation
- rollback execution implementation
- report serialization
- report deserialization
- report persistence implementation
- report rendering implementation
- report cleanup implementation

Instead, it coordinates application use cases by composing
specialized subsystem functions.

Application Handler Flow:
main.py
→ application handler
→ specialized subsystems
→ persistence and presentation

Supported Handlers:
- handle_move
- handle_report
- handle_rollback

Design Principles:
- application-level orchestration
- separation of concerns
- explicit dependency injection
- minimal business logic
- deterministic workflow coordination
- composition-root friendly
- subsystem ownership preservation

IMPORTANT:
This module coordinates workflows.

It does NOT:
- own runtime configuration
- parse command-line arguments
- implement specialized subsystem behavior
- directly mutate application persistence
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from core.contracts import (
    ExecutionReport,
    RollbackReport
)

from core.events import (
    DISCOVERY_FAILED,
    MOVE_COMPLETE,
    MOVE_START,
    PLAN_READY,
    REPORT_COMPLETE,
    REPORT_SKIPPED,
    REPORT_START
)

from tasks.cleanup.cleaner import (
    clear_application_logs,
    delete_report_by_reference,
    delete_reports_by_scope
)

from tasks.discovery.coordinator import discover_files

from tasks.execution.mover import move_files
from tasks.execution.planner import build_execution_plan

from tasks.reporting.generator import (
    build_discovery_report,
    build_execution_report,
    build_planning_report
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

from tasks.reporting.saver import save_report

from tasks.rollback.coordinator import rollback_latest_execution

from utils.logger import log_error, log_info


# -------------------------------------------------
# CLEANUP SCOPES
# -------------------------------------------------
REPORT_DELETION_SCOPES = {
    "executions",
    "rollbacks",
    "all"
}


# -------------------------------------------------
# PUBLIC: Move handler
# -------------------------------------------------
def handle_move(
    path: str,
    dry_run: bool,
    folder_prefix: str,
    reports_directory: str,
    execution_reports_directory: str
) -> None:
    """
    Executes the complete file organization workflow.

    Workflow:
    discovery
    → execution planning
    → filesystem execution or simulation
    → report generation
    → report persistence
    → CLI rendering

    IMPORTANT:
    Specialized behavior remains delegated to its owning
    subsystem. This handler only coordinates the workflow.
    """

    log_info(
        f"{MOVE_START} | "
        f"dry_run={dry_run}"
    )

    # -------------------------------------------------
    # STEP 1: DISCOVERY
    # -------------------------------------------------
    discovery_result = discover_files(
        path
    )

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
    # STEP 4: BUILD EXECUTION REPORT
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
# PUBLIC: Report handler
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
    Routes report presentation and persistence cleanup workflows.

    Supported actions:
    - no action:
        render the latest execution report
    - list:
        render unified chronological report history
    - numeric index:
        render a report selected from history
    - report identifier:
        render a report selected by identifier
    - clear <reference>:
        delete reports or clear application logs

    IMPORTANT:
    This function only selects the required report workflow.
    Each workflow remains coordinated by a dedicated private
    handler.
    """

    log_info(
        f"{REPORT_START} | "
        f"action={action or 'latest'} "
        f"reference={reference}"
    )

    if action == "list":

        _handle_report_list(
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory
        )

        return

    if action == "clear":

        _handle_report_clear(
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory,
            logs_directory,
            log_filename,
            reference
        )

        return

    _handle_report_show(
        reports_directory,
        execution_reports_directory,
        rollback_reports_directory,
        action,
        reference
    )


# -------------------------------------------------
# PUBLIC: Rollback handler
# -------------------------------------------------
def handle_rollback(
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str,
    dry_run: bool
) -> None:
    """
    Executes the complete rollback workflow.

    Workflow:
    latest execution report loading
    → rollback planning
    → rollback execution or simulation
    → rollback report persistence
    → CLI rendering

    IMPORTANT:
    Rollback behavior remains delegated to the rollback
    subsystem. This handler only coordinates the workflow.
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
# PRIVATE: Handle report list
# -------------------------------------------------
def _handle_report_list(
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str
) -> None:
    """
    Loads and renders unified chronological report history.
    """

    history_items = list_report_history(
        reports_directory,
        execution_reports_directory,
        rollback_reports_directory
    )

    if not history_items:

        _render_empty_report_history()

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


# -------------------------------------------------
# PRIVATE: Handle report cleanup
# -------------------------------------------------
def _handle_report_clear(
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str,
    logs_directory: str,
    log_filename: str,
    reference: str | None
) -> None:
    """
    Routes individual, scoped, and log cleanup workflows.
    """

    if reference is None:

        _render_missing_cleanup_reference()

        log_info(
            f"{REPORT_SKIPPED} | "
            "reason=missing_cleanup_reference "
            "action=clear"
        )

        return

    if reference == "logs":

        _handle_log_cleanup(
            logs_directory,
            log_filename
        )

        return

    if reference in REPORT_DELETION_SCOPES:

        _handle_scoped_report_cleanup(
            reference,
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory
        )

        return

    _handle_single_report_cleanup(
        reference,
        reports_directory,
        execution_reports_directory,
        rollback_reports_directory
    )


# -------------------------------------------------
# PRIVATE: Handle report presentation
# -------------------------------------------------
def _handle_report_show(
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str,
    action: str | None,
    reference: str | None
) -> None:
    """
    Loads and renders the latest or selected persisted report.
    """

    if reference is not None:

        _render_invalid_report_command()

        log_info(
            f"{REPORT_SKIPPED} | "
            f"reason=unexpected_report_reference "
            f"action={action} "
            f"reference={reference}"
        )

        return

    if action is None:

        report = load_latest_execution_report(
            reports_directory,
            execution_reports_directory
        )

        report_reference = "latest"

    else:

        report = load_report_by_reference(
            action,
            reports_directory,
            execution_reports_directory,
            rollback_reports_directory
        )

        report_reference = action

    if report is None:

        log_info(
            f"{REPORT_SKIPPED} | "
            f"reason=report_not_found "
            f"reference={report_reference}"
        )

        if action is None:

            _render_missing_latest_execution_report()

        else:

            _render_invalid_report_reference()

        return

    report_type = _render_report_contract(
        report
    )

    if report_type is None:

        return

    log_info(
        f"{REPORT_COMPLETE} | "
        f"type={report_type} "
        f"reference={report_reference}"
    )


# -------------------------------------------------
# PRIVATE: Handle application log cleanup
# -------------------------------------------------
def _handle_log_cleanup(
    logs_directory: str,
    log_filename: str
) -> None:
    """
    Clears the persisted application log file.
    """

    logs_cleared = clear_application_logs(
        logs_directory,
        log_filename
    )

    if not logs_cleared:

        _render_missing_application_logs()

        log_info(
            f"{REPORT_SKIPPED} | "
            "reason=log_file_not_found "
            "action=clear "
            "scope=logs"
        )

        return

    _render_cleared_application_logs(
        logs_directory,
        log_filename
    )

    log_info(
        f"{REPORT_COMPLETE} | "
        "action=clear "
        "scope=logs"
    )


# -------------------------------------------------
# PRIVATE: Handle scoped report cleanup
# -------------------------------------------------
def _handle_scoped_report_cleanup(
    scope: str,
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str
) -> None:
    """
    Deletes persisted reports matching a supported scope.
    """

    deleted_items = delete_reports_by_scope(
        scope,
        reports_directory,
        execution_reports_directory,
        rollback_reports_directory
    )

    if not deleted_items:

        _render_empty_report_cleanup(
            scope
        )

        log_info(
            f"{REPORT_SKIPPED} | "
            f"reason=no_matching_reports "
            f"action=clear "
            f"scope={scope}"
        )

        return

    render_deleted_reports(
        deleted_items,
        scope
    )

    log_info(
        f"{REPORT_COMPLETE} | "
        f"action=clear "
        f"scope={scope} "
        f"deleted={len(deleted_items)}"
    )


# -------------------------------------------------
# PRIVATE: Handle individual report cleanup
# -------------------------------------------------
def _handle_single_report_cleanup(
    reference: str,
    reports_directory: str,
    execution_reports_directory: str,
    rollback_reports_directory: str
) -> None:
    """
    Deletes one persisted report by index or identifier.
    """

    deleted_item = delete_report_by_reference(
        reference,
        reports_directory,
        execution_reports_directory,
        rollback_reports_directory
    )

    if deleted_item is None:

        _render_invalid_report_reference()

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


# -------------------------------------------------
# PRIVATE: Render report contract
# -------------------------------------------------
def _render_report_contract(
    report: ExecutionReport | RollbackReport
) -> str | None:
    """
    Selects the renderer for a supported report contract.

    RETURNS:
        str:
            rendered report type

        None:
            if the contract type is unsupported
    """

    if isinstance(
        report,
        ExecutionReport
    ):

        render_execution_report(
            report
        )

        return "execution"

    if isinstance(
        report,
        RollbackReport
    ):

        render_rollback_report(
            report
        )

        return "rollback"

    log_error(
        f"{REPORT_SKIPPED} | "
        "reason=unsupported_report_contract "
        f"type={type(report).__name__}"
    )

    return None


# -------------------------------------------------
# PRIVATE: Render empty report history
# -------------------------------------------------
def _render_empty_report_history() -> None:
    """
    Renders feedback when no persisted reports are available.
    """

    print()
    print("Reports")
    print("-------")
    print()
    print("No reports found.")
    print()


# -------------------------------------------------
# PRIVATE: Render invalid report reference
# -------------------------------------------------
def _render_invalid_report_reference() -> None:
    """
    Renders feedback for an invalid report index or identifier.
    """

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


# -------------------------------------------------
# PRIVATE: Render missing latest execution report
# -------------------------------------------------
def _render_missing_latest_execution_report() -> None:
    """
    Renders feedback when no execution report is available.
    """

    print()
    print("Report not found.")
    print("No persisted execution reports are available.")
    print()


# -------------------------------------------------
# PRIVATE: Render missing cleanup reference
# -------------------------------------------------
def _render_missing_cleanup_reference() -> None:
    """
    Renders feedback when report clear receives no target.
    """

    print()
    print("Missing report index, identifier, or scope.")
    print()
    print("Use:")
    print()
    print(
        "    python3 main.py report clear "
        "<index_or_identifier>"
    )
    print("    python3 main.py report clear executions")
    print("    python3 main.py report clear rollbacks")
    print("    python3 main.py report clear all")
    print("    python3 main.py report clear logs")
    print()
    print("Available reports can be viewed with:")
    print()
    print("    python3 main.py report list")
    print()


# -------------------------------------------------
# PRIVATE: Render invalid report command
# -------------------------------------------------
def _render_invalid_report_command() -> None:
    """
    Renders supported report command forms.
    """

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


# -------------------------------------------------
# PRIVATE: Render missing application logs
# -------------------------------------------------
def _render_missing_application_logs() -> None:
    """
    Renders feedback when no application log file exists.
    """

    print()
    print("Logs not found.")
    print("No persisted application log file is available.")
    print()


# -------------------------------------------------
# PRIVATE: Render cleared application logs
# -------------------------------------------------
def _render_cleared_application_logs(
    logs_directory: str,
    log_filename: str
) -> None:
    """
    Renders application log cleanup confirmation.
    """

    print()
    print("Cleared Logs")
    print("------------")
    print()
    print(
        f"File: {logs_directory}/{log_filename}"
    )
    print()


# -------------------------------------------------
# PRIVATE: Render empty report cleanup
# -------------------------------------------------
def _render_empty_report_cleanup(
    scope: str
) -> None:
    """
    Renders feedback when no reports match a cleanup scope.
    """

    print()
    print("No reports deleted.")
    print(
        f"No persisted reports matched "
        f"the '{scope}' scope."
    )
    print()