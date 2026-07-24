# -------------------------------------------------
# DISCOVERY COORDINATOR
# -------------------------------------------------
"""
Smart File Organizer - Discovery Coordinator

This module acts as the orchestration layer of the discovery subsystem.

Responsibilities:
- Coordinate discovery pipeline execution
- Integrate scanner, filter, and classifier modules
- Apply discovery filtering rules
- Apply classification rules
- Build reusable classification lookup structures
- Normalize classified discovery output
- Produce discovery-stage result contracts
- Consume trusted discovery and configuration contracts
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
→ discovery result

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
- Reusable classification lookup structures

Contract Usage:
This module consumes trusted discovery and configuration contracts
before producing a validated DiscoveryResult consumed by downstream
execution systems.

Output Contract:
Returns a DiscoveryResult containing:
- classified discovery data
- skipped discovery items with reasons

Example:

DiscoveryResult(
    classified_data={
        "images": [],
        "documents": [],
        "videos": [],
        "others": [],
        "directories": []
    },
    skipped_items=[
        DiscoverySkippedItem(
            name=".DS_Store",
            source_path="/path/.DS_Store",
            reason="hidden_file"
        )
    ]
)

IMPORTANT:
Configured categories are generated dynamically from config.yaml.

Reserved system categories:
- others
- directories

Failure Contract:
- returns None if discovery pipeline fails
- guarantees stable discovery results on successful execution
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
from core.contracts import (
    RawDiscoveryDataset,
    ClassifiedDiscovery,
    DiscoveredItem,
    DiscoverySkippedItem,
    DiscoveryResult
)

from utils.logger import log_info, log_warning
from utils.config_loader import get_config

from tasks.discovery.scanner import scan_directory
from tasks.discovery.filter import should_skip_item
from tasks.discovery.classifier import (
    build_extension_index,
    classify_file
)

from core.events import (
    DISCOVERY_START,
    DISCOVERY_COMPLETE,
    DISCOVERY_SKIP,
    DISCOVERY_FALLBACK
)


# -------------------------------------------------
# PUBLIC: Discovery pipeline
# -------------------------------------------------
def discover_files(path: str) -> DiscoveryResult | None:
    """
    Executes full discovery pipeline.
    """

    log_info(
        f"{DISCOVERY_START} | "
        f"path={path}"
    )

    # -------------------------------------------------
    # CONFIGURATION
    # -------------------------------------------------
    # get_config() returns a validated AppConfig contract.
    # Downstream discovery components can trust its structure.
    config = get_config()
    categories = config.categories

    # -------------------------------------------------
    # CLASSIFICATION LOOKUP INDEX
    # -------------------------------------------------
    # Configured extensions are normalized once per discovery
    # execution instead of once for every discovered file.
    extension_index = build_extension_index(
        categories
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
    # Categories are generated dynamically from AppConfig
    # to preserve config-driven architecture.
    result: ClassifiedDiscovery = {
        category: []
        for category in categories
    }

    # -------------------------------------------------
    # RESERVED SYSTEM CATEGORIES
    # -------------------------------------------------
    # These categories are enforced internally and are
    # intentionally NOT configurable.
    result["others"] = []
    result["directories"] = []

    skipped_items: list[DiscoverySkippedItem] = []

    # -------------------------------------------------
    # PROCESS DISCOVERED ITEMS
    # -------------------------------------------------
    for item in discovered_items:

        # -------------------------------------------------
        # CONTRACTED DISCOVERY ENTITY
        # -------------------------------------------------
        # scanner.py returns validated DiscoveredItem objects.
        item: DiscoveredItem

        name = item.name
        full_path = item.full_path

        # -------------------------------------------------
        # FILTERING
        # -------------------------------------------------
        skip, reason = should_skip_item(
            item,
            config
        )

        if skip:

            skipped_items.append(
                DiscoverySkippedItem(
                    name=name,
                    source_path=full_path,
                    reason=reason
                )
            )

            log_info(
                f"{DISCOVERY_SKIP} | "
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
                extension_index
            )

            # -------------------------------------------------
            # CLASSIFICATION FALLBACK SAFETY
            # -------------------------------------------------
            # Defensive fallback boundary.
            # Keeps discovery output stable even if classification
            # behavior changes in the future.
            if category not in result:

                log_warning(
                    f"{DISCOVERY_FALLBACK} | "
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
        f"skipped={len(skipped_items)}"
    )

    log_info(
        f"{DISCOVERY_COMPLETE} | "
        + " ".join(summary_parts)
    )

    return DiscoveryResult(
        classified_data=result,
        skipped_items=skipped_items
    )