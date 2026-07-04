# -------------------------------------------------
# SMART FILE ORGANIZER - CONFIGURATION LOADER
# -------------------------------------------------
"""
This module is responsible for safely loading, validating,
normalizing, and caching application configuration.

UPDATED ARCHITECTURE (IMPORTANT):
-------------------------------------------------
This module is now the ONLY translator between:
    config.yaml  →  AppConfig (typed contract)

It no longer exposes raw dictionaries to the system.

PRIMARY RESPONSIBILITIES:
- Load YAML configuration from disk
- Validate minimal schema integrity
- Transform raw YAML into AppConfig contract
- Ensure CategoryConfig normalization
- Cache validated AppConfig for runtime reuse

ARCHITECTURE ROLE:
-------------------------------------------------
This module is the single source of truth for configuration
parsing and validation.

Downstream modules MUST ONLY consume:
    AppConfig

They must NOT:
- parse YAML
- access dict-based config
- implement fallback logic
- validate schema structure

CONFIGURATION GUARANTEES:
-------------------------------------------------
The module ensures:
- fully typed AppConfig output
- safe fallback AppConfig if loading fails
- normalized CategoryConfig structures
- deterministic configuration behavior

FAILURE HANDLING STRATEGY:
-------------------------------------------------
If loading or validation fails:
- system falls back to safe AppConfig
- structured logging is emitted
- system continues operating safely

DESIGN PRINCIPLES:
-------------------------------------------------
- contract-first architecture
- strong typing over dicts
- deterministic transformation pipeline
- defensive parsing
- centralized configuration authority
"""

# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import os
import yaml

from utils.logger import log_info, log_warning, log_error

from core.events import (
    CONFIG_GET_START,
    CONFIG_GET_COMPLETE,
    CONFIG_LOAD_START,
    CONFIG_LOAD_SUCCESS,
    CONFIG_LOAD_FAILED,
    CONFIG_INVALID,
    CONFIG_WARNING,
    CONFIG_FALLBACK_USED
)

from core.contracts import AppConfig, CategoryConfig


# -------------------------------------------------
# CONFIG PATH
# -------------------------------------------------
CONFIG_PATH = os.path.abspath(
    os.path.join(
        os.path.dirname(__file__),
        "..",
        "config.yaml"
    )
)


# -------------------------------------------------
# CONFIG CACHE
# -------------------------------------------------
_config_cache: AppConfig | None = None


# -------------------------------------------------
# INTERNAL: SAFE DEFAULT CONFIG (typed fallback)
# -------------------------------------------------
def _build_default_config() -> AppConfig:
    """
    Creates a safe fallback configuration using AppConfig contract.

    IMPORTANT:
    This is the ONLY fallback mechanism in the system.
    """
    return AppConfig(
        folder_prefix="smartorg",
        dry_run=False,
        ignore_hidden_files=True,
        ignore_symlinks=True,
        reports_directory="reports",
        execution_reports_directory="executions",
        categories={}
    )


# -------------------------------------------------
# INTERNAL: VALIDATE & NORMALIZE CONFIG
# -------------------------------------------------
def _validate_config(config: dict) -> AppConfig:
    """
    Validates and normalizes a raw YAML configuration.

    The resulting configuration is always returned as an AppConfig
    instance.

    Invalid category definitions are skipped individually while the
    remaining configuration continues to be processed safely.
    """

    if not isinstance(config, dict):
        log_error(
            f"{CONFIG_INVALID} | "
            "reason=invalid_root_type"
        )
        return _build_default_config()

    # -------------------------------------------------
    # BASIC FIELDS (DEFENSIVE VALIDATION)
    # -------------------------------------------------
    folder_prefix = config.get("folder_prefix", "smartorg")
    dry_run = config.get("dry_run", False)
    ignore_hidden_files = config.get("ignore_hidden_files", True)
    ignore_symlinks = config.get("ignore_symlinks", True)
    reports_directory = config.get("reports_directory", "reports")
    execution_reports_directory = config.get(
        "execution_reports_directory",
        "executions"
    )

    # type safety (IMPORTANT)
    if not isinstance(folder_prefix, str):

        log_error(
            f"{CONFIG_INVALID} | "
            f"key=folder_prefix "
            f"reason=not_string"
        )

        folder_prefix = "smartorg"

    if not isinstance(dry_run, bool):

        log_error(
            f"{CONFIG_INVALID} | "
            f"key=dry_run "
            f"reason=not_boolean"
        )

        dry_run = False

    if not isinstance(ignore_hidden_files, bool):

        log_error(
            f"{CONFIG_INVALID} | "
            f"key=ignore_hidden_files "
            f"reason=not_boolean"
        )

        ignore_hidden_files = True

    if not isinstance(ignore_symlinks, bool):

        log_error(
            f"{CONFIG_INVALID} | "
            f"key=ignore_symlinks "
            f"reason=not_boolean"
        )

        ignore_symlinks = True

    if not isinstance(reports_directory, str):

        log_error(
            f"{CONFIG_INVALID} | "
            f"key=reports_directory "
            f"reason=not_string"
        )

        reports_directory = "reports"

    if not isinstance(execution_reports_directory, str):

        log_error(
            f"{CONFIG_INVALID} | "
            f"key=execution_reports_directory "
            f"reason=not_string"
        )

        execution_reports_directory = "executions"

    # -----------------------------
    # CATEGORIES
    # -----------------------------
    raw_categories = config.get("categories", {})
    categories: dict[str, CategoryConfig] = {}

    if isinstance(raw_categories, dict):

        for name, cat in raw_categories.items():

            # -------------------------------------------------
            # VALIDATE CATEGORY NAME
            # -------------------------------------------------
            if not isinstance(name, str):

                log_error(
                    f"{CONFIG_INVALID} | "
                    f"key=categories "
                    f"reason=invalid_category_name"
                )

                continue

            # -------------------------------------------------
            # VALIDATE CATEGORY STRUCTURE
            # -------------------------------------------------
            if not isinstance(cat, dict):

                log_error(
                    f"{CONFIG_INVALID} | "
                    f"key=categories "
                    f"category={name} "
                    f"reason=invalid_category_structure"
                )

                continue

            try:

                categories[name] = CategoryConfig(
                    description=cat.get("description", ""),
                    extensions=cat.get("extensions", [])
                )

            except Exception as e:

                log_error(
                    f"{CONFIG_INVALID} | "
                    f"key=categories "
                    f"category={name} "
                    f"reason=invalid_category_structure",
                    error=e
                )

                continue

    else:

        log_error(
            f"{CONFIG_INVALID} | "
            f"key=categories "
            f"reason=categories_not_dict"
        )

    # -------------------------------------------------
    # CONFIG WARNING (EMPTY CATEGORIES)
    # -------------------------------------------------
    if not categories:

        log_warning(
            f"{CONFIG_WARNING} | "
            f"key=categories "
            f"reason=empty_categories"
        )

    # -------------------------------------------------
    # BUILD FINAL APP CONFIG (SAFE GUARD)
    # -------------------------------------------------
    try:

        return AppConfig(
            folder_prefix=folder_prefix,
            dry_run=dry_run,
            ignore_hidden_files=ignore_hidden_files,
            ignore_symlinks=ignore_symlinks,
            reports_directory=reports_directory,
            execution_reports_directory=execution_reports_directory,
            categories=categories
        )

    except Exception as e:

        log_error(
            f"{CONFIG_FALLBACK_USED} | "
            f"reason=appconfig_invalid",
            error=e
        )

        return _build_default_config()


# -------------------------------------------------
# INTERNAL: LOAD YAML
# -------------------------------------------------
def _load_yaml() -> dict | None:
    try:

        log_info(
            f"{CONFIG_LOAD_START} | "
            f"path={CONFIG_PATH}"
        )

        with open(CONFIG_PATH, "r") as file:
            config = yaml.safe_load(file)

        log_info(
            f"{CONFIG_LOAD_SUCCESS} | "
            f"path={CONFIG_PATH}"
        )

        return config

    except FileNotFoundError:

        log_error(
            f"{CONFIG_LOAD_FAILED} | "
            f"reason=file_not_found"
        )

        return None

    except yaml.YAMLError as e:

        log_error(
            f"{CONFIG_LOAD_FAILED} | "
            f"reason=yaml_error",
            error=e
        )

        return None

    except Exception as e:

        log_error(
            f"{CONFIG_LOAD_FAILED} | "
            f"reason=unexpected_error",
            error=e
        )

        return None


# -------------------------------------------------
# PUBLIC API
# -------------------------------------------------
def get_config() -> AppConfig:
    global _config_cache

    if _config_cache is not None:
        return _config_cache

    log_info(
        f"{CONFIG_GET_START} | "
        f"path={CONFIG_PATH}"
    )

    raw_config = _load_yaml()

    # -----------------------------
    # FALLBACK HANDLING
    # -----------------------------
    if raw_config is None:

        log_error(
            f"{CONFIG_FALLBACK_USED} | "
            f"reason=load_failed"
        )

        _config_cache = _build_default_config()

        return _config_cache

    config = _validate_config(raw_config)

    _config_cache = config

    log_info(
        f"{CONFIG_GET_COMPLETE} | "
        f"path={CONFIG_PATH}"
    )

    return _config_cache