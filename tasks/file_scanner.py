# -------------------------------------------------
# FILE SCANNER MODULE
# -------------------------------------------------
# Responsibility:
# - Orchestrate directory scanning
# - Apply filtering rules (via file_filters)
# - Apply classification rules (via file_classification)
# - Build structured dataset for mover layer
#
# This module contains NO business logic.

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
# Import required libraries
import os

# Import modules from the project
from utils.logger import log_info, log_warning, log_error
from utils.config_loader import get_config
from tasks.file_filter import should_skip_item
from tasks.file_classificator import classify_file


# -------------------------------------------------
# FILE SCANNER MODULE (OUTPUT-SECURE)
# -------------------------------------------------
def scan_and_classify(path: str):
    """
    Scans a directory and returns SAFE structured classification output.

    OUTPUT CONTRACT:
        Always returns a fixed schema with safe fallback handling.
    """

    # -------------------------------------------------
    # LOAD CONFIGURATION
    # -------------------------------------------------
    config = get_config() or {}

    categories = config.get("categories") or {}

    ignore_hidden = config.get(
        "ignore_hidden_files",
        True
    )

    ignore_symlinks = config.get(
        "ignore_symlinks",
        True
    )

    log_info(f"scan_start | path={path}")

    # -------------------------------------------------
    # FIXED OUTPUT SCHEMA (NEVER CHANGES)
    # -------------------------------------------------
    # Stable scanner contract shared with:
    # - execution_planner.py
    # - future reporting systems
    result = {
        "images": [],
        "documents": [],
        "videos": [],
        "others": [],
        "directories": []
    }

    skipped_total = 0

    # -------------------------------------------------
    # DIRECTORY ACCESS
    # -------------------------------------------------
    try:
        items = os.listdir(path)

        log_info(
            f"scan_items | count={len(items)}"
        )

        # Empty directory is valid behavior
        if not items:

            log_info(
                f"scan_empty | path={path}"
            )

    # -------------------------------------------------
    # DIRECTORY ACCESS FAILURE
    # -------------------------------------------------
    except Exception as e:

        log_error(
            f"scan_error | "
            f"reason=os_error "
            f"path={path}",
            error=e
        )

        return None

    # -------------------------------------------------
    # ITEM ITERATION
    # -------------------------------------------------
    for item in items:

        full_path = os.path.join(path, item)

        # -------------------------------------------------
        # FILTERING LAYER
        # -------------------------------------------------
        skip, reason = should_skip_item(
            item,
            full_path,
            ignore_hidden,
            ignore_symlinks
        )

        if skip:

            skipped_total += 1

            log_info(
                f"scan_skip | "
                f"reason={reason} "
                f"source_path={full_path}"
            )

            continue

        # -------------------------------------------------
        # DIRECTORY DETECTION
        # -------------------------------------------------
        if os.path.isdir(full_path):

            result["directories"].append(item)

            continue

        # -------------------------------------------------
        # FILE CLASSIFICATION
        # -------------------------------------------------
        if os.path.isfile(full_path):

            category = classify_file(
                item,
                categories
            )

            # -------------------------------------------------
            # CLASSIFICATION SAFETY VALIDATION
            # -------------------------------------------------
            # Prevent malformed classifier output from
            # corrupting scanner contract structure.
            if category not in result:

                log_warning(
                    f"scan_classification_fallback | "
                    f"reason=unknown_category "
                    f"file={item} "
                    f"received_category={category}"
                )

                category = "others"

            result[category].append(item)

            continue

        # -------------------------------------------------
        # UNSUPPORTED FILESYSTEM ENTITY
        # -------------------------------------------------
        entity_type = type(full_path).__name__

        log_warning(
            f"scan_skip_item | "
            f"reason=unsupported_type "
            f"source_path={full_path} "
            f"entity_type={entity_type}"
        )

    # -------------------------------------------------
    # FINAL SUMMARY
    # -------------------------------------------------
    log_info(
        f"scan_complete | "
        f"images={len(result['images'])} "
        f"documents={len(result['documents'])} "
        f"videos={len(result['videos'])} "
        f"others={len(result['others'])} "
        f"directories={len(result['directories'])} "
        f"skipped={skipped_total}"
    )

    return result