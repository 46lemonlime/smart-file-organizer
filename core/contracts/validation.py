# -------------------------------------------------
# SMART FILE ORGANIZER - CONTRACT VALIDATION
# -------------------------------------------------
"""
Shared validation helpers for Smart File Organizer contracts.

PURPOSE:
- Centralize primitive contract validation
- Eliminate duplicated validation logic
- Provide consistent validation behavior across contracts

IMPORTANT:
These helpers validate structural integrity only.

They intentionally contain NO:
- business logic
- filesystem logic
- configuration logic
- pipeline logic
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from pathlib import Path

# -------------------------------------------------
# VALIDATE NON-EMPTY STRING
# -------------------------------------------------
def validate_non_empty_string(
    value,
    field_name: str
):
    """
    Validates that a contract field contains
    a non-empty string value.
    """

    if not isinstance(value, str):

        raise TypeError(
            f"{field_name} must be str "
            f"(received {type(value).__name__})"
        )

    if not value.strip():

        raise ValueError(
            f"{field_name} cannot be empty"
        )


# -------------------------------------------------
# VALIDATE LIST TYPE
# -------------------------------------------------
def validate_list_type(
    value,
    field_name: str
):
    """
    Validates that a contract field contains a list.
    """

    if not isinstance(value, list):

        raise TypeError(
            f"{field_name} must be list "
            f"(received {type(value).__name__})"
        )


# -------------------------------------------------
# VALIDATE DICTIONARY TYPE
# -------------------------------------------------
def validate_dict_type(
    value,
    field_name: str
):
    """
    Validates that a contract field contains a dictionary.
    """

    if not isinstance(value, dict):

        raise TypeError(
            f"{field_name} must be dict "
            f"(received {type(value).__name__})"
        )


# -------------------------------------------------
# VALIDATE BOOLEAN TYPE
# -------------------------------------------------
def validate_bool_type(
    value,
    field_name: str
):
    """
    Validates that a contract field contains a boolean.
    """

    if not isinstance(value, bool):

        raise TypeError(
            f"{field_name} must be bool "
            f"(received {type(value).__name__})"
        )


# -------------------------------------------------
# VALIDATE NON-NEGATIVE INTEGER
# -------------------------------------------------
def validate_non_negative_int(
    value,
    field_name: str
):
    """
    Validates that a contract field contains
    a non-negative integer.
    """

    if not isinstance(value, int):

        raise TypeError(
            f"{field_name} must be int "
            f"(received {type(value).__name__})"
        )

    if value < 0:

        raise ValueError(
            f"{field_name} cannot be negative"
        )


# -------------------------------------------------
# VALIDATE PATH TYPE
# -------------------------------------------------
def validate_path_type(
    value,
    field_name: str
):
    """
    Validates that a contract field contains a Path instance.
    """

    if not isinstance(value, Path):

        raise TypeError(
            f"{field_name} must be Path "
            f"(received {type(value).__name__})"
        )