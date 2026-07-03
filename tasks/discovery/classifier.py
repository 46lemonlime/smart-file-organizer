"""
Smart File Organizer - File Classification Engine

This module acts as the classification layer of the discovery subsystem.

Responsibilities:
- Normalize file extensions
- Classify files using config-driven rules
- Provide deterministic category assignment
- Preserve classification contract guarantees

Architecture Role:
This file intentionally contains NO logic related to:
- filesystem scanning
- file filtering
- execution planning
- filesystem mutations
- pipeline orchestration

Instead, it functions as a pure classification layer
responsible for mapping filenames to semantic categories
defined by the application configuration.

Classification Overview:
filename
→ extension normalization
→ config-driven lookup
→ category assignment

Input Contract:
Consumes:
- validated filename
- validated CategoryConfig mapping

Output Contract:
Returns a category name.

Failure Contract:
- consumes trusted pipeline contracts
- returns "others" for unknown extensions
- guarantees deterministic classification

Design Principles:
- deterministic classification
- config-driven behavior
- trusted pipeline contracts
- contract-first architecture
- stable output guarantees

Observability:
Classification is intentionally silent.
Unknown extensions deterministically fall back
to the "others" category.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
# Import standard library dependencies
import os

# Import internal project modules
from core.contracts import CategoryConfig


# -------------------------------------------------
# HELPER: Normalize extensions
# -------------------------------------------------
def normalize_extension(
    ext: str
) -> str | None:
    """
    Normalizes file extensions for deterministic comparison.
    Returns:
        Normalized extension or None if invalid.
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
# PUBLIC: Classify file
# -------------------------------------------------
def classify_file(
    filename: str,
    categories: dict[str, CategoryConfig]
) -> str:
    """
    Assigns a category to a file using config-driven
    extension matching.

    Returns:
        Category name or "others".
    """

    # -------------------------------------------------
    # EXTENSION EXTRACTION
    # -------------------------------------------------
    # Filename is guaranteed by the discovery contract.
    ext = os.path.splitext(filename)[1]

    normalized_ext = normalize_extension(ext)

    # -------------------------------------------------
    # NO EXTENSION FALLBACK
    # -------------------------------------------------
    # Files without a valid extension are intentionally
    # grouped into the generic "others" category.
    if not normalized_ext:
        return "others"

    # -------------------------------------------------
    # CONFIG-DRIVEN LOOKUP
    # -------------------------------------------------
    for category_name, category_config in categories.items():

        # -------------------------------------------------
        # EXTENSION MATCHING
        # -------------------------------------------------
        for extension in category_config.extensions:

            if normalized_ext == normalize_extension(extension):
                return category_name
    
    # -------------------------------------------------
    # FALLBACK CATEGORY
    # -------------------------------------------------
    # Unknown extensions are intentionally grouped
    # into the generic "others" category.
    return "others"