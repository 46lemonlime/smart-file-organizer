# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
# Import standard library dependencies
import os

# Import internal project modules
from utils.logger import log_info, log_warning, log_error
from utils.config_loader import get_config


# -------------------------------------------------
# HELPER: Detect hidden files (config-aware)
# -------------------------------------------------
def is_hidden_file(filename, ignore_hidden: bool):
    """
    Determines whether a file should be treated as hidden.

    Hidden files are ignored when enabled in configuration,
    and typically include system or metadata files such as:

    - .DS_Store (macOS system file)
    - .env (environment configuration)
    - .gitignore / .git (version control metadata)

    This behavior is controlled by:
    ignore_hidden_files (config.yaml)
    """

    # Hidden files are only ignored if config allows it
    return ignore_hidden and filename.startswith(".")


# -------------------------------------------------
# CLASSIFICATION LOGIC (CONFIG DRIVEN)
# -------------------------------------------------
def classify_file(filename, categories: dict):
    """
    Assigns a category to a file based on its extension.

    Classification rules are defined in config.yaml

    Fallback behavior:
    - If no rule matches → assign to "others"
    """

    ext = os.path.splitext(filename)[1].lower()

    # Safety: handle missing or invalid config
    if not categories:
        return "others"

    # -------------------------------------------------
    # CONFIG-DRIVEN LOOKUP
    # -------------------------------------------------
    for category, extensions in categories.items():

        # Expected structure:
        # category:
        #   description: ...
        #   extensions: [...]

        # Defensive check for malformed config
        if not isinstance(extensions, list):
            continue

        if ext in extensions:
            return category

    # Fallback category for unknown file types
    return "others"


# -------------------------------------------------
# SCAN + CLASSIFY DIRECTORY
# -------------------------------------------------
def scan_and_classify(path):
    """
    Scans a directory and builds a structured representation
    of its contents.

    Pipeline:
        1. Read directory contents
        2. Filter hidden/system files (config-driven)
        3. Classify files using config rules
        4. Separate directories from files

    Output format:
    {
        <category>: [...],
        others: [...],
        directories: [...]
    }
    """

    # Load configuration once per scan
    config = get_config() or {}

    categories = config.get("categories", {})
    ignore_hidden = config.get("ignore_hidden_files", True)

    log_info(f"scan_start | path={path}")

    # -------------------------------------------------
    # RESULT STRUCTURE INITIALIZATION
    # -------------------------------------------------
    # NOTE:
    # Categories are dynamic (config-driven),
    # but we initialize known categories + fallback.
    result = {
        "images": [],
        "documents": [],
        "videos": [],
        "others": [],
        "directories": []
    }

    skipped_hidden = 0

    # -------------------------------------------------
    # DIRECTORY ACCESS
    # -------------------------------------------------
    try:
        # Attempt to read directory contents
        # This may fail due to:
        # - invalid path
        # - permission restrictions
        # - filesystem issues
        items = os.listdir(path)

        log_info(f"scan_items | count={len(items)}")
        
        # Edge case: directory exists but contains no items
        if not items:
            log_warning(f"scan_empty | path={path}")
    
    except Exception as e:
        # Critical failure: cannot proceed without directory access
        # Returning None signals upstream logic to abort safely
        log_error(f"scan_error | path={path} error={e}")
        return None

    # -------------------------------------------------
    # ITEM PROCESSING LOOP
    # -------------------------------------------------
    for item in items:

        # STEP 1: Hidden file filtering (config-driven)
        if is_hidden_file(item, ignore_hidden):
            skipped_hidden += 1
            continue

        full_path = os.path.join(path, item)

        # STEP 2: Directory detection
        if os.path.isdir(full_path):
            result["directories"].append(item)

        # STEP 3: File classification (config-driven)
        elif os.path.isfile(full_path):
            category = classify_file(item, categories)
            result[category].append(item)

        # STEP 4: Unsupported filesystem objects
        else:
            log_warning(f"scan_skip_item | path={full_path}")

    # -------------------------------------------------
    # FINAL SUMMARY LOG
    # -------------------------------------------------
    log_info(
        f"scan_complete | "
        f"images={len(result['images'])} "
        f"documents={len(result['documents'])} "
        f"videos={len(result['videos'])} "
        f"others={len(result['others'])} "
        f"directories={len(result['directories'])} "
        f"hidden_skipped={skipped_hidden}"
    )

    return result