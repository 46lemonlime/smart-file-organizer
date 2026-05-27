"""
Smart File Organizer - Discovery Coordinator

This module acts as the orchestration layer of the discovery subsystem.

Responsibilities:
- Coordinate discovery pipeline execution
- Integrate scanner, filter, and classifier modules
- Apply discovery filtering rules
- Apply classification rules
- Normalize classified discovery output
- Enforce discovery contract consistency
- Provide discovery-level observability

Architecture Role:
This file intentionally contains NO logic related to:
- raw filesystem access
- filesystem mutations
- execution planning
- file movement operations

Instead, it functions as a discovery coordinator responsible for
managing execution flow between specialized discovery components.

Discovery Pipeline Overview:
filesystem scanning
→ filtering
→ classification
→ normalized structured output

Discovery Components:
- scanner.py:
    Raw filesystem discovery
- filter.py:
    Skip/filter decision engine
- classifier.py:
    Config-driven file classification

Design Principles:
- Separation of concerns
- Deterministic pipeline coordination
- Controlled subsystem boundaries
- Stable discovery contracts
- Config-driven behavior
- Structured observability

Contract Enforcement:
This module validates and normalizes discovery output before
passing data into downstream execution systems.

Output Contract:
Returns classified discovery data using a dynamic
config-driven structure.

Example:
{
    "images": [],
    "documents": [],
    "videos": [],
    "others": [],
    "directories": []
}

IMPORTANT:
Configured categories are generated dynamically from config.yaml.

Reserved system categories:
- others
- directories

Failure Contract:
- returns None if discovery pipeline fails
- guarantees stable structure on successful execution
- isolates discovery-stage failures

Observability:
Structured logs are emitted throughout execution to provide:
- pipeline traceability
- discovery visibility
- classification diagnostics
- failure localization
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
from contracts import (
    RawDiscoveryDataset,
    ClassifiedDiscovery,
    DiscoveredItem
)

from utils.logger import log_info, log_warning
from utils.config_loader import get_config

from tasks.discovery.scanner import scan_directory
from tasks.discovery.filter import should_skip_item
from tasks.discovery.classifier import classify_file


# -------------------------------------------------
# PUBLIC: Discovery pipeline
# -------------------------------------------------
def discover_files(path: str) -> ClassifiedDiscovery | None:
    """
    Executes full discovery pipeline.
    """

    config = get_config() or {}

    categories = config.get("categories") or {}

    ignore_hidden = config.get(
        "ignore_hidden_files",
        True
    )

    ignore_symlinks = config.get(
        "ignore_symlinks",
        True
    )

    # -------------------------------------------------
    # RAW DISCOVERY
    # -------------------------------------------------
    discovered_items: RawDiscoveryDataset | None = (
        scan_directory(path)
    )

    if discovered_items is None:
        return None

    # -------------------------------------------------
    # DYNAMIC OUTPUT SCHEMA
    # -------------------------------------------------
    # Categories are generated dynamically from config
    # to preserve config-driven architecture.
    result: ClassifiedDiscovery = {
        category: []
        for category in categories.keys()
    }

    # -------------------------------------------------
    # RESERVED SYSTEM CATEGORIES
    # -------------------------------------------------
    # These categories are enforced internally and are
    # intentionally NOT configurable.
    result["others"] = []
    result["directories"] = []

    skipped_total = 0

    # -------------------------------------------------
    # PROCESS DISCOVERED ITEMS
    # -------------------------------------------------
    for item in discovered_items:

        # -------------------------------------------------
        # CONTRACTED DISCOVERY ENTITY
        # -------------------------------------------------
        # scanner.py guarantees DiscoveredItem structure.
        item: DiscoveredItem

        name = item.name
        full_path = item.full_path

        # -------------------------------------------------
        # FILTERING
        # -------------------------------------------------
        skip, reason = should_skip_item(
            name,
            full_path,
            ignore_hidden,
            ignore_symlinks
        )

        if skip:

            skipped_total += 1

            log_info(
                f"discovery_skip | "
                f"reason={reason} "
                f"source_path={full_path}"
            )

            continue

        # -------------------------------------------------
        # DIRECTORY HANDLING
        # -------------------------------------------------
        if item.is_directory:

            result["directories"].append(name)

            continue

        # -------------------------------------------------
        # FILE CLASSIFICATION
        # -------------------------------------------------
        if item.is_file:

            category = classify_file(
                name,
                categories
            )

            # -------------------------------------------------
            # CLASSIFICATION FALLBACK SAFETY
            # -------------------------------------------------
            # Prevent malformed classifier output from
            # corrupting discovery contract structure.
            if category not in result:

                log_warning(
                    f"discovery_fallback | "
                    f"reason=unknown_category "
                    f"file={name} "
                    f"received_category={category}"
                )

                category = "others"

            result[category].append(name)

    # -------------------------------------------------
    # FINAL SUMMARY
    # -------------------------------------------------
    summary_parts = [
        f"{category}={len(files)}"
        for category, files in result.items()
    ]

    summary_parts.append(
        f"skipped={skipped_total}"
    )

    log_info(
        "discovery_complete | "
        + " ".join(summary_parts)
    )

    return result