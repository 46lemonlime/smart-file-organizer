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
import inspect
import os
import uuid

from core.paths import (
    LOG_FILE_PATH,
    LOGS_DIRECTORY,
)

# Session identifier for correlating logs
SESSION_ID = str(uuid.uuid4())[:8]


# -------------------------------------------------
# INTERNAL: get caller module name
# -------------------------------------------------
def _get_caller_module() -> str:
    """
    Returns normalized caller module name.

    Examples:
    - __main__ → MAIN
    - tasks.file_scanner → FILE_SCANNER
    """

    stack = inspect.stack()

    for frame_info in stack:
        module = inspect.getmodule(frame_info.frame)

        if module and module.__name__ != __name__:
            name = module.__name__.split(".")[-1].upper()

            if name == "__MAIN__":
                return "MAIN"

            return name

    return "UNKNOWN"


# -------------------------------------------------
# INTERNAL: ensure log directory exists
# -------------------------------------------------
def _ensure_log_directory() -> None:
    """
    Ensures log directory exists before writing logs.
    """

    os.makedirs(
        LOGS_DIRECTORY,
        exist_ok=True
    )


# -------------------------------------------------
# INTERNAL: sanitize structured values
# -------------------------------------------------
def _sanitize_log_value(value) -> str:
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
# INTERNAL: write log entry
# -------------------------------------------------
def _write_log(
        level: str,
        message: str
    ) -> None:
    """
    Writes formatted log entry into log file.

    Logging failures should NEVER crash application flow.
    """

    try:

        _ensure_log_directory()

        module = _get_caller_module()

        # Cleaner ISO timestamp
        timestamp = datetime.datetime.now().isoformat(timespec="seconds")

        # Defensive normalization
        message = str(message)

        line = f"[{timestamp}][{SESSION_ID}][{level}][{module}] {message}\n"

        with open(LOG_FILE_PATH, "a", encoding="utf-8") as file:
            file.write(line)

    except Exception as e:
        # Final fallback protection
        print(f"[LOGGER_FAILURE] {type(e).__name__}: {e}")


# -------------------------------------------------
# PUBLIC: INFO log
# -------------------------------------------------
def log_info(message: str) -> None:
    """
    General operational logging.
    """

    _write_log("INFO", message)


# -------------------------------------------------
# PUBLIC: WARNING log
# -------------------------------------------------
def log_warning(message: str) -> None:
    """
    Recoverable or non-critical issues.
    """

    _write_log("WARN", message)


# -------------------------------------------------
# PUBLIC: ERROR log
# -------------------------------------------------
def log_error(
        message: str, 
        error: Exception | None = None
    ) -> None:
    """
    Failure and exception logging.
    """

    final_message = str(message)

    # Optional structured exception enrichment
    if error is not None:

        final_message += (
            f" | exception={type(error).__name__}"
        )

        if str(error):
            safe_details = _sanitize_log_value(error)

            final_message += (
                f" | details={safe_details}"
            )

    _write_log("ERROR", final_message)