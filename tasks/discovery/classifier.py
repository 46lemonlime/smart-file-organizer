"""
Smart File Organizer - File Classification Engine

This module acts as the classification layer of the discovery subsystem.

Responsibilities:
- Normalize file extensions
- Build normalized extension lookup indexes
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
configured categories
→ extension index construction

filename
→ extension normalization
→ indexed category lookup
→ category assignment

Input Contract:
Consumes:
- validated filename
- validated CategoryConfig mapping
- normalized extension lookup index

Output Contract:
Returns:
- normalized extension lookup index
- category name

Failure Contract:
- consumes trusted pipeline contracts
- ignores invalid configured extensions
- returns "others" for unknown extensions
- guarantees deterministic classification

Design Principles:
- deterministic classification
- config-driven behavior
- trusted pipeline contracts
- contract-first architecture
- stable output guarantees
- precomputed lookup structures

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
# PUBLIC: Build extension lookup index
# -------------------------------------------------
def build_extension_index(
    categories: dict[str, CategoryConfig]
) -> dict[str, str]:
    """
    Builds a normalized extension-to-category lookup index.

    The first configured category containing an extension
    retains ownership of that extension.

    Returns:
        Mapping of normalized extensions to category names.
    """

    extension_index: dict[str, str] = {}

    for category_name, category_config in categories.items():

        for extension in category_config.extensions:

            normalized_extension = normalize_extension(
                extension
            )

            if normalized_extension:
                extension_index.setdefault(
                    normalized_extension,
                    category_name
                )

    return extension_index


# -------------------------------------------------
# PUBLIC: Classify file
# -------------------------------------------------
def classify_file(
    filename: str,
    extension_index: dict[str, str]
) -> str:
    """
    Assigns a category to a file using a precomputed
    normalized extension lookup index.

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
    # INDEXED CATEGORY LOOKUP
    # -------------------------------------------------
    return extension_index.get(
        normalized_ext,
        "others"
    )