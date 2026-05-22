# -------------------------------------------------
# EXECUTION PLANNER
# -------------------------------------------------
"""
This module builds a deterministic execution plan BEFORE filesystem operations.

ARCHITECTURAL ROLE:
- Defines WHAT should happen
- Does NOT execute anything
- Does NOT modify filesystem

OUTPUT CONTRACT:
Each operation is fully executable by file_mover.py without transformation.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
# Import required libraries
import os

# Import modules from the project
from utils.logger import log_info, log_warning


def build_execution_plan(path, classified_data, folder_prefix):
    """
    Builds deterministic filesystem execution plan.
    """

    log_info("plan_build_start")

    # -------------------------------------------------
    # PLAN STRUCTURE
    # -------------------------------------------------
    # Central deterministic execution contract
    # shared between:
    # - dry-run mode
    # - real execution mode
    plan = {
        "folders_to_create": [],
        "operations": [],
        "skipped": []
    }

    # -------------------------------------------------
    # INPUT VALIDATION
    # -------------------------------------------------
    # Defensive validation for scanner contract integrity
    if not isinstance(classified_data, dict):

        log_warning(
            f"plan_invalid | "
            f"reason=invalid_classified_data "
            f"received_type={type(classified_data).__name__}"
        )

        return plan

    planned_folders = set()

    # -------------------------------------------------
    # CATEGORY ITERATION
    # -------------------------------------------------
    for category, files in classified_data.items():

        # Internal scanner-only tracking bucket
        if category == "directories":
            continue

        # -------------------------------------------------
        # CATEGORY VALIDATION
        # -------------------------------------------------
        if not isinstance(files, list):

            log_warning(
                f"plan_skip | "
                f"reason=invalid_category_files "
                f"category={category} "
                f"received_type={type(files).__name__}"
            )

            continue

        # Ignore empty categories
        if not files:
            continue

        # -------------------------------------------------
        # DESTINATION RESOLUTION
        # -------------------------------------------------
        folder_name = f"{folder_prefix}-{category}"

        destination_folder = os.path.join(
            path,
            folder_name
        )

        # -------------------------------------------------
        # FOLDER REGISTRATION
        # -------------------------------------------------
        # Register once to avoid duplicate creation entries
        if destination_folder not in planned_folders:

            planned_folders.add(destination_folder)

            if not os.path.exists(destination_folder):

                plan["folders_to_create"].append(
                    destination_folder
                )

        # -------------------------------------------------
        # FILE ITERATION
        # -------------------------------------------------
        for file in files:

            # -------------------------------------------------
            # FILENAME VALIDATION
            # -------------------------------------------------
            if not isinstance(file, str) or not file.strip():

                plan["skipped"].append({
                    "reason": "invalid_filename",
                    "file": file,
                    "category": category
                })

                continue

            # -------------------------------------------------
            # PATH RESOLUTION
            # -------------------------------------------------
            source_path = os.path.join(path, file)

            destination_path = os.path.join(
                destination_folder,
                file
            )

            # -------------------------------------------------
            # SOURCE VALIDATION
            # -------------------------------------------------
            if not os.path.exists(source_path):

                plan["skipped"].append({
                    "reason": "file_missing",
                    "file": file,
                    "category": category,
                    "source_path": source_path
                })

                continue

            # -------------------------------------------------
            # FINAL EXECUTION CONTRACT
            # -------------------------------------------------
            # Structure consumed directly by file_mover.py
            # without additional transformation.
            plan["operations"].append({
                "category": category,
                "file": file,
                "source_path": source_path,
                "destination_path": destination_path,
                "folder_name": folder_name
            })

    # -------------------------------------------------
    # FINAL SUMMARY
    # -------------------------------------------------
    log_info(
        f"plan_build_complete | "
        f"folders={len(plan['folders_to_create'])} "
        f"operations={len(plan['operations'])} "
        f"skipped={len(plan['skipped'])}"
    )

    return plan