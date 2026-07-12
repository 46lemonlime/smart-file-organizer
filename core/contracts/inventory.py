# -------------------------------------------------
# SMART FILE ORGANIZER - INVENTORY CONTRACTS
# -------------------------------------------------
"""
Shared inventory contracts for Smart File Organizer.

PURPOSE:
- Define the structures produced during filesystem discovery
- Represent discovered items and classified inventory
- Provide stable discovery contracts across the application

ARCHITECTURE ROLE:
This module acts as the canonical source of truth for:
- discovered filesystem items
- classified inventory
- discovery skipped items
- aggregated discovery results

IMPORTANT:
These contracts contain NO:
- filesystem scanning
- filtering logic
- classification logic
- business logic

Discovery behavior is implemented by the discovery subsystem.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from dataclasses import dataclass
from typing import TypeAlias

from .validation import (
    validate_bool_type,
    validate_dict_type,
    validate_list_type,
    validate_non_empty_string,
)


# -------------------------------------------------
# DISCOVERED ITEM CONTRACT
# -------------------------------------------------
@dataclass
class DiscoveredItem:
    """
    Represents a raw filesystem entity discovered during scanning.

    CONTRACT GUARANTEES:
    - name is a non-empty string
    - full_path is a non-empty string
    - is_file is boolean
    - is_directory is boolean

    IMPORTANT:
    This contract intentionally contains NO business logic.
    Only structural validation is enforced here.
    """

    name: str
    full_path: str
    is_file: bool
    is_directory: bool

    def __post_init__(self):

        validate_non_empty_string(
            self.name,
            "name"
        )

        validate_non_empty_string(
            self.full_path,
            "full_path"
        )

        validate_bool_type(
            self.is_file,
            "is_file"
        )

        validate_bool_type(
            self.is_directory,
            "is_directory"
        )


# -------------------------------------------------
# RAW DISCOVERY DATASET CONTRACT
# -------------------------------------------------
RawDiscoveryDataset: TypeAlias = list[DiscoveredItem]


# -------------------------------------------------
# CLASSIFIED DISCOVERY DATASET CONTRACT
# -------------------------------------------------
ClassifiedDiscovery: TypeAlias = dict[str, list[str]]


# -------------------------------------------------
# DISCOVERY SKIPPED ITEM CONTRACT
# -------------------------------------------------
@dataclass
class DiscoverySkippedItem:
    """
    Represents an item skipped during the discovery stage.

    CONTRACT GUARANTEES:
    - name is a non-empty string
    - source_path is a non-empty string
    - reason is a non-empty string

    IMPORTANT:
    This contract preserves item-level discovery skip
    traceability for reporting and future audit workflows.
    """

    name: str
    source_path: str
    reason: str

    def __post_init__(self):

        validate_non_empty_string(
            self.name,
            "name"
        )

        validate_non_empty_string(
            self.source_path,
            "source_path"
        )

        validate_non_empty_string(
            self.reason,
            "reason"
        )


# -------------------------------------------------
# DISCOVERY RESULT CONTRACT
# -------------------------------------------------
@dataclass
class DiscoveryResult:
    """
    Represents the complete discovery-stage result.

    CONTRACT GUARANTEES:
    - classified_data is ClassifiedDiscovery
    - skipped_items is list[DiscoverySkippedItem]

    IMPORTANT:
    This contract preserves discovery metadata that does not
    belong inside ClassifiedDiscovery itself.
    """

    classified_data: ClassifiedDiscovery
    skipped_items: list[DiscoverySkippedItem]

    def __post_init__(self):

        validate_dict_type(
            self.classified_data,
            "classified_data"
        )

        for category, files in self.classified_data.items():

            validate_non_empty_string(
                category,
                "classified_data category"
            )

            validate_list_type(
                files,
                "classified_data files"
            )

            for file in files:

                validate_non_empty_string(
                    file,
                    "classified_data file"
                )

        validate_list_type(
            self.skipped_items,
            "skipped_items"
        )

        for skipped_item in self.skipped_items:

            if not isinstance(
                skipped_item,
                DiscoverySkippedItem
            ):

                raise TypeError(
                    "skipped_items must contain "
                    "DiscoverySkippedItem objects"
                )