#Import necessary libraries
import os

def scan_directory(path):
    """
    Phase 3:
    Scans a directory and returns structured data about its contents.

    Output format:
    {
        "files": [...],
        "directories": [...]
    }
    """

    # Debug message to confirm which directory is being scanned
    print(f"Scanning directory: {path}")

    # Lists to store results separately
    files = []
    directories = []

    try:
        # Retrieve all items (files, folders, etc.) in the given path
        items = os.listdir(path)

    except Exception as e:
        # Handle cases where the directory cannot be accessed
        print(f"[ERROR] Cannot access directory: {e}")
        return None

    # Iterate through each item found in the directory
    for item in items:

        # Build the full path of the item
        full_path = os.path.join(path, item)

        # Check if item is a directory
        if os.path.isdir(full_path):
            directories.append(item)

        # Check if item is a file
        elif os.path.isfile(full_path):
            files.append(item)

        # Catch-all for anything else (symlinks, system artifacts, etc.)
        else:
            # For Phase 3 we ignore these, but keep structure for future expansion
            pass

    # Return structured data for use in later phases (classification, reports, etc.)
    return {
        "files": files,
        "directories": directories
    }

'''
#Previous version of move_files (Phase 2)

def move_files(path):
    #This function will eventually contain the logic to move files based on configuration rules.
    print(f"Scanning directory: {path}")

    #1. Get everything inside the folder
    items = os.listdir(path)

    #2. Print the list of items (files and folders)
    print("Items found in the directory:")
    for item in items:
        full_path = os.path.join(path, item)
        if os.path.isdir(full_path):
            print(f"- directory: {item}")
        elif os.path.isfile(full_path):
            print(f"- file: {item}")

    print(f"[PHASE 1] move_files called with path: {path}")
    print("[PHASE 1] Not implemented yet.")


'''