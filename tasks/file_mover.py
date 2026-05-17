# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
# Import necessary libraries
import os
import shutil

# Import modules from the project
from utils.logger import log_info, log_warning, log_error
from utils.config_loader import get_config


# -------------------------------------------------
# FILE MOVING ENGINE
# -------------------------------------------------
def move_files(path, classified_data, dry_run):
    """
    Executes file organization process based on classified input.

    Responsibilities:
    - Create destination folders
    - Move files into structured directories
    - Log execution events

    Supports:
    - Normal mode (real filesystem operations)
    - Dry-run mode (simulation without changes)
    """

    # Execution mode is controlled externally via the dry_run flag.
    # This function strictly respects the provided value.

    # Load configuration (centralized settings)
    config = get_config() or {}

    # Folder prefix (fallback ensures backward compatibility)
    prefix = config.get("folder_prefix", "smartorg")

    log_info(f"move_start | path={path} dry_run={dry_run}")

    # Defensive check for data integrity
    if not isinstance(classified_data, dict):
        log_error("move_error | reason=invalid_classified_data")
        return

    # -------------------------------------------------
    # MOVE SUMMARY TRACKING
    # -------------------------------------------------
    # These counters track execution results for observability
    # and final reporting.
    total_moved = 0
    category_summary = {}

    # -------------------------------------------------
    # Iterate through classified categories
    # -------------------------------------------------
    for category, files in classified_data.items():

        # Ignore directory entries (not part of movement phase)
        if category == "directories":
            continue

        # Skip empty categories
        if not files:
            continue

        # Initialize category counter (only if category has files)
        category_summary[category] = 0

        # -------------------------------------------------
        # Create destination folder name with prefix
        # Example: smartorg-images, smartorg-documents
        # -------------------------------------------------
        folder_name = f"{prefix}-{category}"
        destination_folder = os.path.join(path, folder_name)

        # Create folder if it does not exist
        if not os.path.exists(destination_folder):

            # Dry-run: simulate folder creation
            if dry_run:
                log_info(f"folder_create_simulation | folder={folder_name}")
            else:
                os.makedirs(destination_folder)
                log_info(f"folder_created | folder={folder_name}")

        # -------------------------------------------------
        # Move each file into its category folder
        # -------------------------------------------------
        for file in files:

            source_path = os.path.join(path, file)
            destination_path = os.path.join(destination_folder, file)

            # Safety check: Ensure file still exists before moving
            if not os.path.exists(source_path):
                log_warning(f"file_missing | file={file}")
                continue

            try:
                # Dry-run: simulate file movement
                if dry_run:
                    log_info(
                        f"file_move_simulation | file={file} destination={folder_name}"
                    )
                else:
                    shutil.move(source_path, destination_path)
                    log_info(
                        f"file_moved | file={file} destination={folder_name}"
                    )

                # Summary tracking update (only counts actual moves, not dry-run simulations)
                total_moved += 1
                category_summary[category] += 1

            except Exception as e:
                log_error(f"move_failed | file={file} error={e}")

    # -------------------------------------------------
    # FINAL MOVE SUMMARY
    # -------------------------------------------------
    summary_parts = [
        f"total={total_moved}",
    ]

    # Add per-category breakdown to summary
    for cat, count in category_summary.items():
        summary_parts.append(f"{cat}={count}")

    # Execution state (kept at end for consistency)
    summary_parts.append(f"dry_run={dry_run}")

    log_info("move_summary | " + " ".join(summary_parts))
    
    log_info("move_complete")