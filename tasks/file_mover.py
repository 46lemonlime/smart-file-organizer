#Import necessary libraries
import os
import shutil


# -------------------------------------------------
# Configuration (temporary - will move to config.yaml)
# -------------------------------------------------
PREFIX = "smartorg"


def move_files(path, classified_data):
    """
    Phase 4: File moving engine

    Takes classified file structure and physically
    organizes files into prefixed folders inside the
    target directory.
    """

    print(f"\n[PHASE 4] Organizing files in: {path}")

    # -------------------------------------------------
    # Iterate through classified categories
    # -------------------------------------------------
    for category, files in classified_data.items():

        # We do NOT move directories in this phase
        if category == "directories":
            continue

        # Skip empty categories (nothing to process)
        if not files:
            continue

        # -------------------------------------------------
        # Create destination folder name with prefix
        # Example: smartorg-images, smartorg-documents
        # -------------------------------------------------
        folder_name = f"{PREFIX}-{category}"
        destination_folder = os.path.join(path, folder_name)

        # Create folder if it doesn't exist
        if not os.path.exists(destination_folder):
            os.makedirs(destination_folder)
            print(f"[CREATE] Folder created: {folder_name}")

        # -------------------------------------------------
        # Move each file into its category folder
        # -------------------------------------------------
        for file in files:

            # Build full source and destination paths
            source_path = os.path.join(path, file)
            destination_path = os.path.join(destination_folder, file)

            # Safety check: ensure file still exists
            if os.path.exists(source_path):

                # Move file
                shutil.move(source_path, destination_path)
                print(f"[MOVE] {file} → {folder_name}/")

            else:
                print(f"[WARNING] File not found: {file}")