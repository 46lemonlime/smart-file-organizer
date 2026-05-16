#Import necessary libraries
import os

#import modules from the project
from utils.logger import log_info, log_warning, log_error

# -----------------------------
# Helper: Detect hidden files
# -----------------------------
def is_hidden_file(filename):
    """
    Determines whether a file should be considered hidden.

    In this project, hidden files are defined as:
    - Files starting with '.' (Unix/macOS convention)

    These are excluded from processing to avoid:
    - system files (.DS_Store)
    - environment files (.env)
    - git metadata (.gitignore, .git)
    """

    return filename.startswith(".")

# -----------------------------
# Classify a single file
# -----------------------------
def classify_file(filename):
    """
    Assigns a category to a file based on its extension.

    This is used to group files into logical folders
    during the organization phase.

    Categories:
    - images
    - documents
    - videos
    - others (fallback group)
    """

    ext = os.path.splitext(filename)[1].lower()

    # Image formats
    if ext in [".png", ".jpg", ".jpeg", ".gif", ".webp"]:
        return "images"

    # Document formats (including archives for now)
    elif ext in [".pdf", ".docx", ".txt", ".md", ".zip"]:
        return "documents"

    # Video formats
    elif ext in [".mp4", ".mov", ".avi", ".mkv"]:
        return "videos"

    # Fallback category for unknown or unsupported types
    else:
        return "others"


# -----------------------------
# Scan + classify directory
# -----------------------------
def scan_and_classify(path):
    """
    Scans a directory and builds a structured representation
    of its contents.

    This is the FIRST stage of the pipeline:

        1. Read directory contents
        2. Filter unwanted files (hidden/system)
        3. Classify files by type
        4. Separate directories from files

    Output format:
    {
        images: [...],
        documents: [...],
        videos: [...],
        others: [...],
        directories: [...]
    }
    """

    # Debug message to confirm which directory is being scanned
    log_info(f"Starting scan for: {path}")

    # Final structured result used by downstream processing
    result = {
        "images": [],
        "documents": [],
        "videos": [],
        "others": [],
        "directories": []
    }

    # Counter for logging skipped hidden files
    skipped_hidden = 0

    try:
        # Retrieve raw directory contents and log the count
        items = os.listdir(path)
        log_info(f"Items found: {len(items)}")
        
        # Edge case: Empty directory (log a warning but continue gracefully)
        if not items:
            log_warning(f"Directory is empty: {path}")

    except Exception as e:
        # Handle permission or invalid path errors
        log_error(f"Cannot access directory: {path} | Error: {e}")
        return None

    # -------------------------------------------------
    # ITEM PROCESSING LOOP
    # -------------------------------------------------
    for item in items:
    
        # STEP 1: Filter hidden files early
        # (prevents unnecessary processing)
        if is_hidden_file(item):
            skipped_hidden += 1
            continue

        # Build full path
        full_path = os.path.join(path, item)

        # STEP 2: Identify directories
        if os.path.isdir(full_path):
            result["directories"].append(item)

        # STEP 3: Identify and classify regular files
        elif os.path.isfile(full_path):
            category = classify_file(item)
            result[category].append(item)

        # STEP 4: Handle unexpected item types (e.g. symbolic links, sockets)
        else:
            log_warning(f"Skipping unsupported item type: {full_path}")

    # -------------------------------------------------
    # FINAL SUMMARY LOG
    # -------------------------------------------------
    log_info(
        f"Scan complete | "
        f"images: {len(result['images'])}, "
        f"documents: {len(result['documents'])}, "
        f"videos: {len(result['videos'])}, "
        f"others: {len(result['others'])}, "
        f"directories: {len(result['directories'])}, "
        f"hidden skipped: {skipped_hidden}"
    )

    return result