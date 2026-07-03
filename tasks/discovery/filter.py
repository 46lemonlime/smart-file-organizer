"""
Smart File Organizer - Discovery Filtering Policy

This module implements the filtering policy layer of the
discovery subsystem.

Responsibilities:
- Apply discovery skip rules
- Handle hidden file filtering
- Handle symbolic link filtering
- Produce deterministic skip decisions

Architecture Role:
This file intentionally contains NO logic related to:
- filesystem scanning
- file classification
- execution planning
- filesystem mutations
- pipeline orchestration

Instead, it acts as the policy layer responsible for
determining whether discovered filesystem entities
should continue through the discovery pipeline.

Input Contract:
Consumes:
- validated DiscoveredItem
- validated AppConfig

Output Contract:
Returns a deterministic skip decision:

(
    skip: bool,
    reason: str | None
)

Failure Contract:
- consumes trusted pipeline contracts
- assumes validated inputs
- guarantees deterministic filtering decisions

Design Principles:
- centralized filtering ownership
- deterministic policy evaluation
- contract-first architecture
- config-driven behavior
- trusted pipeline contracts
- stable filtering decisions

Observability:
Skip reasons are propagated into the structured logging
system by the discovery coordinator.
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
# Import required libraries
import os

from core.contracts import (
    AppConfig,
    DiscoveredItem
)

# -------------------------------------------------
# HELPER: Unified skip decision engine
# -------------------------------------------------
def should_skip_item(
    discovered_item: DiscoveredItem,
    config: AppConfig
) -> tuple[bool, str | None]:
    """
    Determines whether a discovered filesystem entity
    should be skipped according to the configured
    filtering policy.
    """

    # -------------------------------------------------
    # RULE 1: Hidden files
    # -------------------------------------------------
    # Hidden files typically include system metadata:
    # e.g. .DS_Store, .env, .gitignore
    #
    # DiscoveredItem guarantees a valid filename.
    if (
        config.ignore_hidden_files 
        and discovered_item.name.startswith(".")
    ):
        return True, "hidden_file"

    # -------------------------------------------------
    # RULE 2: Symlinks
    # -------------------------------------------------
    # Symlinks can point outside the target directory,
    # so we avoid following them for safety reasons.
    #
    # DiscoveredItem guarantees a valid filesystem path.
    if (
        config.ignore_symlinks 
        and os.path.islink(discovered_item.full_path)
    ):
        return True, "symlink"

    # -------------------------------------------------
    # DEFAULT: do not skip
    # -------------------------------------------------
    return False, None