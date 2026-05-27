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
- pipeline coordination

Instead, it functions as a pure filesystem access layer
responsible for exposing raw filesystem entities to higher-level
discovery components.

Discovery Overview:
filesystem access
→ directory enumeration
→ metadata resolution
→ normalized discovery contracts

Output Contract:
Returns normalized discovery entities using shared typed contracts:

[
    DiscoveredItem(
        name="photo.jpg",
        full_path="/downloads/photo.jpg",
        is_file=True,
        is_directory=False
    )
]

Failure Contract:
- returns None on scan failure
- never propagates filesystem exceptions upstream
- guarantees controlled failure behavior

Design Principles:
- Separation of concerns
- Pure filesystem responsibility
- Deterministic discovery behavior
- Defensive filesystem handling
- Reusable discovery foundation
- Stable discovery contracts

Observability:
Structured logs are emitted throughout execution to provide:
- discovery traceability
- filesystem visibility
- scan diagnostics
- failure localization
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import os

from utils.logger import log_info, log_error
from contracts import DiscoveredItem


# -------------------------------------------------
# PUBLIC: Scan directory
# -------------------------------------------------
def scan_directory(path: str) -> list[DiscoveredItem] | None:
    """
    Performs raw filesystem discovery.

    RETURNS:
        list[DiscoveredItem] | None
    """

    log_info(f"scan_start | path={path}")

    try:

        items = os.listdir(path)

        log_info(
            f"scan_items | count={len(items)}"
        )

        # -------------------------------------------------
        # NORMALIZED DISCOVERY OUTPUT
        # -------------------------------------------------
        discovered_items = []

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
            f"scan_complete | discovered={len(discovered_items)}"
        )

        return discovered_items

    except Exception as e:

        log_error(
            f"scan_failed | "
            f"reason=os_error "
            f"path={path}",
            error=e
        )

        return None