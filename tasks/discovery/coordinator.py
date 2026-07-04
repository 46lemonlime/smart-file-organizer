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
- Normalize classified discovery output
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

Contract Usage:
This module consumes trusted discovery and configuration contracts
before passing normalized classified discovery data into downstream
execution systems.

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
from logging import config

from core.contracts import (
    RawDiscoveryDataset,
    ClassifiedDiscovery,
    DiscoveredItem
)

from utils.logger import log_info, log_warning
from utils.config_loader import get_config

from tasks.discovery.scanner import scan_directory
from tasks.discovery.filter import should_skip_item
from tasks.discovery.classifier import classify_file

from core.events import (
    DISCOVERY_START,
    DISCOVERY_COMPLETE,
    DISCOVERY_SKIP,
    DISCOVERY_FALLBACK
)

# -------------------------------------------------
# PUBLIC: Discovery pipeline
# -------------------------------------------------
def discover_files(path: str) -> ClassifiedDiscovery | None:
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

            skipped_total += 1

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
                categories
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
        f"skipped={skipped_total}"
    )

    log_info(
        f"{DISCOVERY_COMPLETE} | "
        + " ".join(summary_parts)
    )
  
    return result