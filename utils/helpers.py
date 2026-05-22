# -------------------------------------------------
# GENERIC HELPERS (CROSS-MODULE UTILITIES)
# -------------------------------------------------
"""
This module is reserved for generic helper functions that are:

- Reusable across multiple modules
- Not tied to a specific domain (e.g. file sorting, moving, classification)
- Free of business logic and side effects where possible

PURPOSE:
- Avoid duplication of low-level utility logic
- Keep domain modules focused on their responsibilities

DO NOT ADD:
- File system logic (belongs in file_mover / file_scanner)
- Classification logic (belongs in file_classification)
- Filtering logic (belongs in file_filters)
- Task orchestration logic

GUIDELINE:
If a function "knows" about:
- files
- categories
- execution flow

→ it does NOT belong here.

EXAMPLES OF VALID HELPERS:
- string normalization
- generic validation utilities
- safe data transformations
- small reusable formatting functions

This file should remain small, stable, and highly reusable.
"""