"""
Smart File Organizer - Filesystem Scanner

This module acts as the low-level filesystem discovery layer
of the discovery subsystem.

Responsibilities:
- Access filesystem safely
- Enumerate directory contents
- Resolve raw filesystem metadata
- Build normalized discovery entities
- Isolate filesystem access concerns

Architecture Role:
This file intentionally contains NO business logic related to:
- file filtering
- file classification
- execution planning
- filesystem mutations
- pipeline orchestration

Instead, it functions as a pure filesystem access layer
responsible for exposing raw filesystem entities to higher-level
discovery components.

Discovery Pipeline:
filesystem access
→ directory enumeration
→ metadata resolution
→ normalized discovery entities

Input Contract:
Consumes:
- filesystem path

Output Contract:
Returns a RawDiscoveryDataset containing normalized
DiscoveredItem entities.

Failure Contract:
- returns None on scan failure
- never propagates filesystem exceptions upstream
- guarantees controlled failure behavior

Design Principles:
- separation of concerns
- filesystem-only responsibility
- deterministic discovery behavior
- defensive filesystem handling
- reusable discovery foundation
- trusted pipeline contracts
- stable discovery structures

Observability:
Structured logs are emitted throughout execution to provide:
- filesystem discovery traceability
- scan visibility
- discovery diagnostics
- failure localization
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import os

from utils.logger import log_info, log_error

from core.events import (
    SCAN_START,
    SCAN_ITEMS,
    SCAN_COMPLETE,
    SCAN_FAILED
)

from core.contracts import (
    DiscoveredItem,
    RawDiscoveryDataset
)

# -------------------------------------------------
# PUBLIC: Scan directory
# -------------------------------------------------
def scan_directory(
    path: str
) -> RawDiscoveryDataset | None:
    """
    Performs raw filesystem discovery.

    RETURNS:
        RawDiscoveryDataset | None
    """

    log_info(f"{SCAN_START} | path={path}")

    try:

        items = os.listdir(path)

        log_info(
            f"{SCAN_ITEMS} | count={len(items)}"
        )

        # -------------------------------------------------
        # NORMALIZED DISCOVERY OUTPUT
        # -------------------------------------------------
        discovered_items: RawDiscoveryDataset = []

        for item in items:

            full_path = os.path.join(path, item)

            discovered_items.append(
                DiscoveredItem(
                    name=item,
                    full_path=full_path,
                    is_file=os.path.isfile(full_path),
                    is_directory=os.path.isdir(full_path)
                )
            )

        log_info(
            f"{SCAN_COMPLETE} | discovered={len(discovered_items)}"
        )

        return discovered_items

    except Exception as e:

        log_error(
            f"{SCAN_FAILED} | "
            f"reason=os_error "
            f"path={path}",
            error=e
        )

        return None