# -------------------------------------------------
# SCANNER
# -------------------------------------------------
SCAN_START = "scan_start | path={path}"
SCAN_COMPLETE = "scan_complete | count={count}"
SCAN_ERROR = "scan_error | reason={reason} path={path}"

# -------------------------------------------------
# PLANNER
# -------------------------------------------------
PLAN_BUILD_START = "plan_build_start"
PLAN_BUILD_COMPLETE = (
    "plan_build_complete | folders={folders} "
    "operations={operations} skipped={skipped}"
)
PLAN_INVALID = "plan_invalid | reason={reason}"

# -------------------------------------------------
# EXECUTION
# -------------------------------------------------
MOVE_START = "move_start | dry_run={dry_run} operations={operations}"
MOVE_COMPLETE = "move_complete"
MOVE_SUMMARY = (
    "move_summary | attempted={attempted} "
    "completed={completed} failed={failed} dry_run={dry_run}"
)

FILE_MOVED = "file_moved | file={file} destination={destination_path}"
FILE_SIMULATION = "file_move_simulation | file={file} destination={destination_path}"

MOVE_FAILED = (
    "move_failed | reason={reason} file={file} "
    "source_path={source_path}"
)

# -------------------------------------------------
# CONFIG
# -------------------------------------------------
CONFIG_INVALID = "config_invalid | key={key} reason={reason}"