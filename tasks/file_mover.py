#Import necessary libraries
import os
import shutil

#import modules from the project
from utils.logger import log_info, log_warning, log_error

# -------------------------------------------------
# Configuration (temporary - will move to config.yaml)
# -------------------------------------------------
PREFIX = "smartorg"


def move_files(path, classified_data):
    """
    File moving engine
    Takes classified file structure and physically
    organizes files into prefixed folders inside the
    target directory.
    """

    log_info(f"Organizing files in: {path}")

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
            log_info(f"[CREATE] Folder created: {folder_name}")

        # -------------------------------------------------
        # Move each file into its category folder
        # -------------------------------------------------
        for file in files:

            # Build full source and destination paths
            source_path = os.path.join(path, file)
            destination_path = os.path.join(destination_folder, file)

            # Safety check: ensure file still exists
            if os.path.exists(source_path):

                try:
                    shutil.move(source_path, destination_path)
                    log_info(f"Moved file: {file} → {folder_name}/")

                except Exception as e:
                    log_error(f"Failed to move {file}: {e}")

            else:
                log_warning(f"File not found during move: {file}")
        
    log_info("File move process completed")