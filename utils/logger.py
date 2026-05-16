# -------------------------------------------------
# IMPORTS
# -------------------------------------------------

# Import required libraries
import datetime
import os
import inspect
import uuid

# -------------------------------------------------
# LOG CONFIGURATION
# -------------------------------------------------

# Folder where logs will be stored
LOG_DIR = "logs"

# Full path to the log file
LOG_FILE = os.path.join(LOG_DIR, "smartorg.log")

#Session ID for correlating logs across a single run (optional, can be used for advanced log analysis)
SESSION_ID = str(uuid.uuid4())[:8]  # e.g. "a1b2c3d4"

# -------------------------------------------------
# INTERNAL: get caller module name for contextual logging
# -------------------------------------------------
def _get_caller_module():
    """
    Returns normalized caller module name for logging.

    Examples:
    - __main__ → MAIN
    - tasks.file_sorter → FILE_SORTER
    """

    stack = inspect.stack()

    # safer: walk upward until we exit logger module
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
def _ensure_log_directory(): #In Python, a leading underscore is a convention that means: “internal use only”.
    """
    Ensures that the logs directory exists before writing logs.

    Why this matters:
    - Fresh installs won't have /logs
    - Deleted folders would otherwise crash logging
    - Keeps logger self-contained and safe
    """

    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)  # creates folder (and parent dirs if needed)


# ----------------------------------------
# Internal function: write log entry
# ----------------------------------------
def _write_log(level: str, message: str):
    """
    Writes a formatted log entry into the log file.

    Each log entry includes:
    - Timestamp (ISO 8601 format)
    - Log level (INFO / WARN / ERROR)
    - Message content
    """

    # Ensure logging directory exists before writing
    _ensure_log_directory()

    # Automatically capture caller module for better log context
    module = _get_caller_module()

    # Create timestamp in ISO format (e.g. 2026-05-15T12:34:56)
    timestamp = datetime.datetime.now().isoformat()

    # Format final log line as: [timestamp][session_id][LEVEL][MODULE] message
    line = f"[{timestamp}][{SESSION_ID}][{level}][{module}] {message}\n"

    # ----------------------------------------
    # Open file in append mode ("a")
    # ----------------------------------------
    # "a" means:
    # - append mode (does NOT overwrite file)
    # - creates file if it doesn't exist
    # - writes at the end of the file
    with open(LOG_FILE, "a") as f:
        f.write(line)

# ----------------------------------------
# Public log: INFO level
# ----------------------------------------
def log_info(message: str):
    """
    Used for general information (normal operations)
    Automatically detects the calling module.
    """
    _write_log("INFO", message)


# ----------------------------------------
# Public log: WARNING level
# ----------------------------------------
def log_warning(message: str):
    """
    Used when something unexpected happens,
    but program can continue safely
    Automatically detects the calling module.
    """
    _write_log("WARN", message)


# ----------------------------------------
# Public log: ERROR level
# ----------------------------------------
def log_error(message: str, error: Exception = None):
    """
    Used when something fails or breaks
    Automatically detects the calling module.
    Adds optional exception context for better debugging.
    """

    # Base message
    final_message = message

    # If an exception is provided, enrich the log
    if error is not None:
        final_message += f" | Exception: {type(error).__name__}"

        # Add actual exception message if available
        if str(error):
            final_message += f" | Details: {str(error)}"

    _write_log("ERROR", final_message)
