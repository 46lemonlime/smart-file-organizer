# -------------------------------------------------
# SMART FILE ORGANIZER - CLI PARSER
# -------------------------------------------------
"""
This module defines the application's command-line interface.

Responsibilities:
- Build the CLI structure
- Define supported commands
- Parse command-line arguments
- Validate CLI syntax
- Return parsed execution arguments
- Parse report history actions, references, and scopes
- Parse cleanup resources and report cleanup targets

Architecture Role:
This module intentionally contains NO logic related to:
- configuration loading
- filesystem discovery
- execution planning
- filesystem mutations
- rollback execution
- report loading
- report history resolution
- report history filtering
- report deletion
- log cleanup
- reporting
- task routing

Instead, it functions as the application's CLI boundary,
responsible only for translating command-line input into a
structured argument namespace.

CLI Flow:
terminal input
→ command parsing
→ argument validation
→ parsed execution arguments

Supported Commands:
- move
- report
- rollback
- cleanup

Report Actions:
- no action:
    display the latest persisted execution report
- list:
    display unified report history
- list executions:
    display execution report history
- list rollbacks:
    display rollback report history
- numeric index:
    select a report from the history list
- report identifier:
    select a report by its timestamp-based identifier

Cleanup Resources:
- report <target>:
    delete a report by index or identifier, or delete reports
    using a supported scope
- log:
    clear the application log
- all:
    clear all persisted reports and application logs

Design Principles:
- CLI-only responsibility
- deterministic argument parsing
- centralized command definitions
- no business logic
- no dependency injection
- composition-root friendly

IMPORTANT:
This module only parses command-line arguments.

It does NOT:
- execute application logic
- resolve report references
- filter report history
- determine report cleanup scope
- delete persisted reports
- clear application logs
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import argparse

from core.metadata import APP_DESCRIPTION


# -------------------------------------------------
# PUBLIC: Parse CLI arguments
# -------------------------------------------------
def parse_args() -> argparse.Namespace:
    """
    Parses application command-line arguments.

    RETURNS:
        argparse.Namespace
    """

    # -------------------------------------------------
    # ROOT PARSER
    # -------------------------------------------------
    parser = argparse.ArgumentParser(
        description=APP_DESCRIPTION
    )

    subparsers = parser.add_subparsers(
        dest="task",
        required=True,
        metavar="command"
    )

    # -------------------------------------------------
    # MOVE COMMAND
    # -------------------------------------------------
    move_parser = subparsers.add_parser(
        "move",
        help="Organize files inside a directory."
    )

    move_parser.add_argument(
        "path",
        type=str,
        help="Target directory."
    )

    move_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate filesystem changes."
    )

    # -------------------------------------------------
    # REPORT COMMAND
    # -------------------------------------------------
    report_parser = subparsers.add_parser(
        "report",
        help="Display persisted reports and report history."
    )

    report_parser.add_argument(
        "reference",
        nargs="?",
        default=None,
        help=(
            "Use 'list', a history index, or a report "
            "identifier. Defaults to the latest persisted "
            "execution report."
        )
    )

    report_parser.add_argument(
        "report_scope",
        nargs="?",
        default=None,
        help=(
            "Optional report history scope used with 'list': "
            "'executions' or 'rollbacks'."
        )
    )

    # -------------------------------------------------
    # ROLLBACK COMMAND
    # -------------------------------------------------
    rollback_parser = subparsers.add_parser(
        "rollback",
        help="Rollback the latest execution."
    )

    rollback_parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Simulate rollback operations."
    )

    # -------------------------------------------------
    # CLEANUP COMMAND
    # -------------------------------------------------
    cleanup_parser = subparsers.add_parser(
        "cleanup",
        help="Delete application-generated persistence artifacts."
    )

    cleanup_subparsers = cleanup_parser.add_subparsers(
        dest="cleanup_resource",
        required=True,
        metavar="resource"
    )

    # -------------------------------------------------
    # CLEANUP REPORT
    # -------------------------------------------------
    cleanup_report_parser = cleanup_subparsers.add_parser(
        "report",
        help="Delete persisted reports."
    )

    cleanup_report_parser.add_argument(
        "cleanup_target",
        type=str,
        help=(
            "Report history index, report identifier, or scope: "
            "'executions', 'rollbacks', or 'all'."
        )
    )

    # -------------------------------------------------
    # CLEANUP LOG
    # -------------------------------------------------
    cleanup_subparsers.add_parser(
        "log",
        help="Clear the application log."
    )

    # -------------------------------------------------
    # CLEANUP ALL
    # -------------------------------------------------
    cleanup_subparsers.add_parser(
        "all",
        help="Delete all persisted reports and clear application logs."
    )

    return parser.parse_args()