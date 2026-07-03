# -------------------------------------------------
# SMART FILE ORGANIZER - APPLICATION METADATA
# -------------------------------------------------
"""
Centralized application metadata and core static constants.

PURPOSE:
- Define canonical application identity
- Centralize version management
- Avoid duplicated hardcoded metadata
- Provide reusable application-wide constants

ARCHITECTURE ROLE:
This module acts as the single source of truth for:
- application name
- semantic version
- startup banners
- future global static metadata

IMPORTANT:
This module is intentionally LIMITED to:
- static application metadata
- non-configurable constants

DO NOT STORE:
- user configuration
- runtime state
- execution data
- environment-dependent values

CONFIG VS METADATA:
- config.yaml:
    User-configurable behavior
- metadata.py:
    Static application identity/constants

DESIGN PRINCIPLES:
- centralized ownership
- deterministic metadata
- reusable constants
- stable application identity
- minimal responsibility surface

FUTURE EXPANSION:
This module may later include:
- supported task registry
- global event namespaces
- application identifiers
- release metadata
"""

# -------------------------------------------------
# APPLICATION IDENTITY
# -------------------------------------------------
APP_NAME = "Smart File Organizer"

# Semantic Versioning (SemVer)
VERSION = "0.8.0"

# Prefixed semantic version label
VERSION_LABEL = f"v{VERSION}"

APP_DESCRIPTION = ("Deterministic filesystem organization CLI")

# Full application banner
APP_BANNER = f"{APP_NAME} {VERSION_LABEL}"

# -------------------------------------------------
# SUPPORTED TASKS 
# ------------------------------------------------- 
SUPPORTED_TASKS = { "move", "report" }