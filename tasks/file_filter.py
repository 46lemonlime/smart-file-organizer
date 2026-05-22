# -------------------------------------------------
# FILE FILTERING MODULE
# -------------------------------------------------
# Responsibility:
# - Centralized pre-processing rules for file skipping
# - Handles hidden files and symlinks
# - Config-driven filtering decisions
# - Returns structured skip reasons for logging
#
# IMPORTANT:
# Skip reasons returned by this module are part of the
# structured logging contract and should remain:
# - machine-readable
# - deterministic
# - stable across modules

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
# Import required libraries
import os


# -------------------------------------------------
# HELPER: Unified skip decision engine
# -------------------------------------------------
def should_skip_item(
    filename: str,
    full_path: str,
    ignore_hidden: bool,
    ignore_symlinks: bool
):
    """
    Determines whether a filesystem item should be skipped.

    Returns:
        tuple:
            (
                skip: bool,
                reason: str | None
            )

    Possible reasons:
    - invalid_filename_type
    - empty_filename
    - invalid_path_type
    - empty_path
    - hidden_file
    - symlink
    """

    # -------------------------------------------------
    # VALIDATION: filename safety
    # -------------------------------------------------
    if not isinstance(filename, str):
        return True, "invalid_filename_type"

    if not filename.strip():
        return True, "empty_filename"

    # -------------------------------------------------
    # VALIDATION: path safety
    # -------------------------------------------------
    if not isinstance(full_path, str):
        return True, "invalid_path_type"

    if not full_path.strip():
        return True, "empty_path"

    # -------------------------------------------------
    # RULE 1: Hidden files
    # -------------------------------------------------
    # Hidden files typically include system metadata:
    # e.g. .DS_Store, .env, .gitignore
    if ignore_hidden and filename.startswith("."):
        return True, "hidden_file"

    # -------------------------------------------------
    # RULE 2: Symlinks
    # -------------------------------------------------
    # Symlinks can point outside the target directory,
    # so we avoid following them for safety reasons.
    if ignore_symlinks and os.path.islink(full_path):
        return True, "symlink"

    # -------------------------------------------------
    # DEFAULT: do not skip
    # -------------------------------------------------
    return False, None