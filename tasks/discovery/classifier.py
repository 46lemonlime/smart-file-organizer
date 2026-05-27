"""
Smart File Organizer - File Classification Engine

This module is responsible for assigning files to logical categories
based on configurable extension rules defined in the system configuration.

Primary Responsibilities:
- Normalize file extensions for consistent comparison
- Perform config-driven file classification
- Provide deterministic category assignment
- Ensure safe fallback behavior for all edge cases
- Maintain structured observability for classification decisions

Architecture Role:
This module acts as the classification engine within the discovery
pipeline, translating raw filenames into semantic categories used by
downstream planning and execution layers.

This module contains NO:
- filesystem scanning logic
- filtering logic
- execution logic
- file movement logic

Classification Philosophy:
- Fully deterministic behavior
- Config-driven rule evaluation
- Defensive handling of malformed inputs
- Guaranteed fallback to "others"
- No exception propagation to upstream layers

Configuration Model:
Categories are defined in config.yaml as:

categories:
  images:
    extensions: [.png, .jpg]

Each category maps to a list of file extensions used for matching.

Failure Handling Strategy:
- Invalid inputs are safely categorized as "others"
- Malformed configuration entries are skipped with warnings
- No runtime exceptions are propagated

Observability:
Classification decisions and config issues are logged using
structured warning logs for debugging and traceability.

Design Principles:
- Deterministic mapping logic
- Config-driven behavior
- Defensive programming
- Stable output guarantees
- Strict separation of concerns
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
# Import standard library dependencies
import os

# Import internal project modules
from utils.logger import log_warning


# -------------------------------------------------
# HELPER: Normalize extensions
# -------------------------------------------------
def normalize_extension(ext: str):
    """
    Normalizes file extensions for consistent comparison.

    Ensures:
    - lowercase
    - starts with '.'

    Examples:
    'JPG'  -> '.jpg'
    '.PNG' -> '.png'
    """

    # -------------------------------------------------
    # VALIDATION: extension type
    # -------------------------------------------------
    if not isinstance(ext, str):
        return None

    ext = ext.lower().strip()

    # -------------------------------------------------
    # VALIDATION: empty extension
    # -------------------------------------------------
    if not ext:
        return None

    # -------------------------------------------------
    # NORMALIZATION
    # -------------------------------------------------
    if not ext.startswith("."):
        ext = "." + ext

    return ext


# -------------------------------------------------
# CLASSIFICATION LOGIC (CONFIG DRIVEN)
# -------------------------------------------------
def classify_file(filename, categories: dict):
    """
    Assigns a category to a file based on extension.

    Classification rules are defined in config.yaml

    SAFETY GUARANTEES:
    - never crashes
    - handles malformed config safely
    - handles malformed filenames safely
    - always returns a valid category
    - deterministic fallback behavior

    FALLBACK:
        unmatched files -> "others"
    """

    # -------------------------------------------------
    # INPUT VALIDATION
    # -------------------------------------------------
    if not isinstance(filename, str):
        log_warning(
            f"classify_skip | "
            f"reason=invalid_filename_type "
            f"file={filename}"
        )
        return "others"

    if not filename.strip():
        log_warning(
            f"classify_skip | "
            f"reason=empty_filename "
            f"file={filename}"
        )
        return "others"

    # -------------------------------------------------
    # EXTENSION EXTRACTION
    # -------------------------------------------------
    try:
        # NOTE:
        # os.path.splitext may fail on malformed paths
        ext = os.path.splitext(filename)[1]

    except Exception:
        log_warning(
            f"classify_skip | "
            f"reason=invalid_path "
            f"file={filename}"
        )
        return "others"

    normalized_ext = normalize_extension(ext)

    # -------------------------------------------------
    # NO EXTENSION FALLBACK
    # -------------------------------------------------
    if not normalized_ext:
        return "others"

    # -------------------------------------------------
    # CONFIG VALIDATION
    # -------------------------------------------------
    if not isinstance(categories, dict) or not categories:

        log_warning(
            f"classify_config_invalid | "
            f"reason=missing_or_invalid_categories "
            f"file={filename}"
        )

        return "others"

    # -------------------------------------------------
    # CONFIG-DRIVEN LOOKUP
    # -------------------------------------------------
    for category, config_entry in categories.items():

        # -------------------------------------------------
        # VALIDATE CATEGORY NAME
        # -------------------------------------------------
        if not isinstance(category, str):

            log_warning(
                f"classify_config_skip | "
                f"reason=invalid_category_name "
                f"category_name={category} "
                f"file={filename}"
            )

            continue

        # -------------------------------------------------
        # VALIDATE CONFIG ENTRY
        # -------------------------------------------------
        if not isinstance(config_entry, dict):

            log_warning(
                f"classify_config_skip | "
                f"reason=invalid_config_entry "
                f"category={category} "
                f"file={filename}"
            )

            continue

        extensions = config_entry.get("extensions")

        # -------------------------------------------------
        # VALIDATE EXTENSIONS LIST
        # -------------------------------------------------
        if not isinstance(extensions, list):

            log_warning(
                f"classify_config_skip | "
                f"reason=invalid_extensions_list "
                f"category={category} "
                f"file={filename}"
            )

            continue

        # -------------------------------------------------
        # EXTENSION MATCHING
        # -------------------------------------------------
        for ext_item in extensions:

            normalized_item = normalize_extension(ext_item)

            # -------------------------------------------------
            # INVALID EXTENSION ENTRY
            # -------------------------------------------------
            if not normalized_item:

                log_warning(
                    f"classify_config_skip | "
                    f"reason=invalid_extension_value "
                    f"category={category} "
                    f"extension={ext_item} "
                    f"file={filename}"
                )

                continue

            # -------------------------------------------------
            # MATCH FOUND
            # -------------------------------------------------
            if normalized_ext == normalized_item:
                return category

    # -------------------------------------------------
    # FALLBACK CATEGORY
    # -------------------------------------------------
    return "others"