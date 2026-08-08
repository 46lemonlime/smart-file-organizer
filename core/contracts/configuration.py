# -------------------------------------------------
# SMART FILE ORGANIZER - CONFIGURATION CONTRACTS
# -------------------------------------------------
"""
Shared configuration contracts for Smart File Organizer.

PURPOSE:
- Define validated runtime configuration
- Centralize configuration structures
- Provide stable configuration contracts across the application

ARCHITECTURE ROLE:
This module acts as the canonical source of truth for:
- application configuration
- category configuration

IMPORTANT:
These contracts contain NO:
- configuration loading
- configuration parsing
- filesystem access
- business logic

Configuration loading and validation are handled by
the configuration subsystem.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from dataclasses import dataclass

from .validation import (
    validate_bool_type,
    validate_dict_type,
    validate_list_type,
    validate_non_empty_string,
)


# -------------------------------------------------
# CATEGORY CONFIG CONTRACT
# -------------------------------------------------
@dataclass
class CategoryConfig:
    """
    Represents a configurable file classification category.

    CONTRACT GUARANTEES:
    - description is a non-empty string
    - extensions is a list[str]
    """

    description: str
    extensions: list[str]

    def __post_init__(self):

        validate_non_empty_string(
            self.description,
            "description"
        )

        validate_list_type(
            self.extensions,
            "extensions"
        )

        for extension in self.extensions:

            validate_non_empty_string(
                extension,
                "extensions item"
            )


# -------------------------------------------------
# APPLICATION CONFIG CONTRACT
# -------------------------------------------------
@dataclass
class AppConfig:
    """
    Represents the validated runtime configuration.

    CONTRACT GUARANTEES:
    - all required configuration values exist
    - downstream modules never require defaults
    - configuration is fully validated
    """

    folder_prefix: str
    dry_run: bool
    ignore_hidden_files: bool
    ignore_symlinks: bool
    categories: dict[str, CategoryConfig]

    def __post_init__(self):

        validate_non_empty_string(
            self.folder_prefix,
            "folder_prefix"
        )

        validate_bool_type(
            self.dry_run,
            "dry_run"
        )

        validate_bool_type(
            self.ignore_hidden_files,
            "ignore_hidden_files"
        )

        validate_bool_type(
            self.ignore_symlinks,
            "ignore_symlinks"
        )

        validate_dict_type(
            self.categories,
            "categories"
        )

        for category_name, category_config in self.categories.items():

            validate_non_empty_string(
                category_name,
                "category name"
            )

            if not isinstance(
                category_config,
                CategoryConfig
            ):

                raise TypeError(
                    "categories must contain "
                    "CategoryConfig objects"
                )