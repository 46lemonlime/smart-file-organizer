# -------------------------------------------------
# STRUCTURED LOGGING CONTRACT
# -------------------------------------------------
"""
All logs in this project MUST follow this format:

    action_name | key=value key=value

Examples:
    scan_start | path=/downloads
    move_failed | reason=file_missing file=test.pdf

Rules:
- Use lowercase snake_case actions
- Use structured key=value metadata
- Avoid free-text production logs
- Keep logs machine-readable and consistent
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import datetime
import inspect
import os
import uuid


# -------------------------------------------------
# LOG CONFIGURATION
# -------------------------------------------------
# Folder where logs are stored
LOG_DIR = "logs"

# Full path to log file
LOG_FILE = os.path.join(LOG_DIR, "smartorg.log")

# Session identifier for correlating logs
SESSION_ID = str(uuid.uuid4())[:8]


# -------------------------------------------------
# INTERNAL: get caller module name
# -------------------------------------------------
def _get_caller_module():
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
def _ensure_log_directory():
    """
    Ensures log directory exists before writing logs.
    """

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)


# -------------------------------------------------
# INTERNAL: sanitize structured values
# -------------------------------------------------
def _sanitize_log_value(value):
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
def _write_log(level: str, message: str):
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

        with open(LOG_FILE, "a", encoding="utf-8") as f:
            f.write(line)

    except Exception as e:
        # Final fallback protection
        print(f"[LOGGER_FAILURE] {type(e).__name__}: {e}")


# -------------------------------------------------
# PUBLIC: INFO log
# -------------------------------------------------
def log_info(message: str):
    """
    General operational logging.
    """

    _write_log("INFO", message)


# -------------------------------------------------
# PUBLIC: WARNING log
# -------------------------------------------------
def log_warning(message: str):
    """
    Recoverable or non-critical issues.
    """

    _write_log("WARN", message)


# -------------------------------------------------
# PUBLIC: ERROR log
# -------------------------------------------------
def log_error(message: str, error: Exception = None):
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