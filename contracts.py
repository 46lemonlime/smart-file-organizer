# -------------------------------------------------
# SMART FILE ORGANIZER - CORE CONTRACTS
# -------------------------------------------------
"""
This module defines the core shared contracts used across
the Smart File Organizer pipeline.

PURPOSE:
- Centralize shared pipeline structures
- Define stable inter-module contracts
- Improve architectural consistency
- Reduce dynamic dictionary usage
- Enable stronger type safety

ARCHITECTURE ROLE:
This module acts as the canonical source of truth for:
- discovery entities
- execution operations
- execution planning structures

IMPORTANT:
These contracts are shared across multiple subsystems:
- discovery
- execution
- reporting (future)

DESIGN PRINCIPLES:
- deterministic structures
- explicit contracts
- strong typing
- reusable pipeline entities
- centralized schema ownership

NOTE:
Contracts should remain:
- lightweight
- stable
- serialization-friendly
- free of business logic
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from dataclasses import dataclass
from typing import Optional, TypeAlias


# -------------------------------------------------
# DISCOVERY CONTRACTS
# -------------------------------------------------
@dataclass
class DiscoveredItem:
    """
    Represents a raw filesystem entity discovered during scanning.
    """

    name: str
    full_path: str
    is_file: bool
    is_directory: bool


# -------------------------------------------------
# DISCOVERY DATASET CONTRACTS
# -------------------------------------------------
# Raw scanner output contract
#
# IMPORTANT:
# This structure is intentionally dynamic because
# discovery entities are generated from filesystem state.
RawDiscoveryDataset: TypeAlias = list[DiscoveredItem]


# Classified discovery output contract
#
# IMPORTANT:
# Categories are intentionally NOT hardcoded here.
#
# The classification system is fully config-driven and
# categories are defined dynamically via config.yaml.
#
# Example:
# {
#     "images": ["photo.jpg"],
#     "documents": ["notes.pdf"],
#     "music": ["song.mp3"]
# }
ClassifiedDiscovery: TypeAlias = dict[str, list[str]]


# -------------------------------------------------
# EXECUTION CONTRACTS
# -------------------------------------------------
@dataclass
class ExecutionOperation:
    """
    Represents a single executable filesystem operation.
    """

    category: str
    file: str
    source_path: str
    destination_path: str
    folder_name: str


# -------------------------------------------------
# EXECUTION SKIP CONTRACT
# -------------------------------------------------
@dataclass
class SkippedOperation:
    """
    Represents a skipped planning operation.
    """

    reason: str
    file: Optional[str] = None
    category: Optional[str] = None
    source_path: Optional[str] = None


# -------------------------------------------------
# EXECUTION PLAN CONTRACT
# -------------------------------------------------
@dataclass
class ExecutionPlan:
    """
    Represents the deterministic execution plan generated
    before filesystem mutations occur.
    """

    folders_to_create: list[str]
    operations: list[ExecutionOperation]
    skipped: list[SkippedOperation]