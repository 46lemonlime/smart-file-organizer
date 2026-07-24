"""
Smart File Organizer - Structured Logging Infrastructure

This module provides the centralized structured logging system used
across the entire application.

Primary Responsibilities:
- Provide standardized structured logging APIs
- Enforce machine-readable log formatting
- Attach execution metadata automatically
- Handle logging fault tolerance
- Maintain session-level execution traceability
- Normalize log output consistency

Architecture Role:
This module acts as the observability infrastructure layer of the system.

All modules depend on this logging contract for:
- operational visibility
- debugging
- execution tracing
- failure diagnostics
- future reporting systems

Logging Philosophy:
- Structured over free-text logging
- Machine-readable log output
- Consistent metadata formatting
- Stable log taxonomy
- Failure-safe logging behavior

Structured Log Contract:
All logs follow the format:

    action_name | key=value key=value

Examples:
    scan_start | path=/downloads
    move_failed | reason=file_missing file=test.pdf

Automatic Metadata:
Each log entry automatically includes:
- timestamp
- session identifier
- severity level
- caller module

Observability Features:
- Session correlation support
- Module ownership visibility
- Structured exception enrichment
- Log sanitization protection
- Failure-safe logging writes

Failure Handling Strategy:
Logging failures must NEVER interrupt application execution.

If the logging system itself fails, execution continues with
fallback console diagnostics.

Design Principles:
- Centralized observability
- Structured logging contracts
- Machine-readable logs
- Failure isolation
- Consistent operational tracing
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import datetime
import os
import sys
import uuid

from core.paths import (
    LOG_FILE_PATH,
    LOGS_DIRECTORY,
)


# -------------------------------------------------
# SESSION STATE
# -------------------------------------------------
# Session identifier for correlating logs.
SESSION_ID = str(uuid.uuid4())[:8]

# Avoids checking or creating the logging directory for every
# individual log entry.
_LOG_DIRECTORY_READY = False


# -------------------------------------------------
# INTERNAL: Get caller module name
# -------------------------------------------------
def _get_caller_module() -> str:
    """
    Returns the normalized caller module name.

    Examples:
    - __main__ → MAIN
    - tasks.file_scanner → FILE_SCANNER

    The expected call chain is:

        caller
        → log_info / log_warning / log_error
        → _write_log
        → _get_caller_module
    """

    try:

        caller_frame = sys._getframe(3)

        module_name = caller_frame.f_globals.get(
            "__name__",
            "UNKNOWN"
        )

        name = module_name.split(".")[-1].upper()

        if name == "__MAIN__":

            return "MAIN"

        return name

    except (ValueError, AttributeError):

        return "UNKNOWN"


# -------------------------------------------------
# INTERNAL: Ensure log directory exists
# -------------------------------------------------
def _ensure_log_directory() -> None:
    """
    Ensures the log directory exists before writing logs.

    The filesystem check is performed only once per process
    after successful directory preparation.
    """

    global _LOG_DIRECTORY_READY

    if _LOG_DIRECTORY_READY:

        return

    os.makedirs(
        LOGS_DIRECTORY,
        exist_ok=True
    )

    _LOG_DIRECTORY_READY = True


# -------------------------------------------------
# INTERNAL: Sanitize structured values
# -------------------------------------------------
def _sanitize_log_value(
    value
) -> str:
    """
    Prevents structured log corruption.

    Normalizes:
    - spaces
    - newlines
    - tabs
    - pipe separators
    """

    value = str(value)

    value = value.replace("\n", "_")
    value = value.replace("\t", "_")
    value = value.replace("|", "_")
    value = value.replace(" ", "_")

    return value


# -------------------------------------------------
# INTERNAL: Write log entry
# -------------------------------------------------
def _write_log(
    level: str,
    message: str
) -> None:
    """
    Writes a formatted log entry into the log file.

    Logging failures must never interrupt application flow.
    """

    try:

        _ensure_log_directory()

        module = _get_caller_module()

        timestamp = datetime.datetime.now().isoformat(
            timespec="milliseconds"
        )

        message = str(message)

        line = (
            f"[{timestamp}]"
            f"[{SESSION_ID}]"
            f"[{level}]"
            f"[{module}] "
            f"{message}\n"
        )

        with open(
            LOG_FILE_PATH,
            "a",
            encoding="utf-8"
        ) as file:

            file.write(line)

    except Exception as error:

        print(
            f"[LOGGER_FAILURE] "
            f"{type(error).__name__}: {error}"
        )


# -------------------------------------------------
# PUBLIC: INFO log
# -------------------------------------------------
def log_info(
    message: str
) -> None:
    """
    Writes a general operational log entry.
    """

    _write_log(
        "INFO",
        message
    )


# -------------------------------------------------
# PUBLIC: WARNING log
# -------------------------------------------------
def log_warning(
    message: str
) -> None:
    """
    Writes a recoverable or non-critical issue.
    """

    _write_log(
        "WARN",
        message
    )


# -------------------------------------------------
# PUBLIC: ERROR log
# -------------------------------------------------
def log_error(
    message: str,
    error: Exception | None = None
) -> None:
    """
    Writes a failure or exception log entry.
    """

    final_message = str(message)

    if error is not None:

        final_message += (
            f" | exception={type(error).__name__}"
        )

        if str(error):

            safe_details = _sanitize_log_value(
                error
            )

            final_message += (
                f" | details={safe_details}"
            )

    _write_log(
        "ERROR",
        final_message
    )