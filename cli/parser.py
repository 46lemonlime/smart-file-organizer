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

Architecture Role:
This module intentionally contains NO logic related to:
- configuration loading
- filesystem discovery
- execution planning
- filesystem mutations
- rollback execution
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

Design Principles:
- CLI-only responsibility
- deterministic argument parsing
- centralized command definitions
- no business logic
- no dependency injection
- composition-root friendly

IMPORTANT:
This module only parses command-line arguments.
It does NOT execute application logic.
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
    subparsers.add_parser(
        "report",
        help="Display the latest execution report."
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

    return parser.parse_args()