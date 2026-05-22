# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
import os
import yaml

from utils.logger import log_info, log_error


# -------------------------------------------------
# CONFIG PATH
# -------------------------------------------------
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")


# -------------------------------------------------
# CONFIG CACHE
# -------------------------------------------------
_config_cache = None


# -------------------------------------------------
# SAFE DEFAULT CONFIG (NEW)
# -------------------------------------------------
# Ensures downstream modules NEVER receive partial configs
DEFAULT_CONFIG = {
    "folder_prefix": "smartorg",
    "dry_run": False,
    "categories": {}
}


# -------------------------------------------------
# INTERNAL: Basic config validation
# -------------------------------------------------
def _validate_config(config):
    """
    Performs lightweight validation of expected config structure.
    Ensures safe types and guarantees full schema completeness.
    """

    # -------------------------------------------------
    # ROOT VALIDATION (ENHANCED)
    # -------------------------------------------------
    if not isinstance(config, dict):
        log_error("config_invalid | reason=invalid_root_type action=default_applied")
        return DEFAULT_CONFIG.copy()

    # -------------------------------------------------
    # FOLDER PREFIX VALIDATION
    # -------------------------------------------------
    if "folder_prefix" in config and not isinstance(config["folder_prefix"], str):
        log_error("config_invalid | key=folder_prefix type=string action=default_applied")
        config["folder_prefix"] = DEFAULT_CONFIG["folder_prefix"]

    # -------------------------------------------------
    # DRY RUN VALIDATION
    # -------------------------------------------------
    if "dry_run" in config and not isinstance(config["dry_run"], bool):
        log_error("config_invalid | key=dry_run type=bool action=default_applied")
        config["dry_run"] = DEFAULT_CONFIG["dry_run"]

    # -------------------------------------------------
    # CATEGORIES VALIDATION (NEW HARDENING)
    # -------------------------------------------------
    categories = config.get("categories", DEFAULT_CONFIG["categories"])

    if categories is None or not isinstance(categories, dict):
        log_error("config_invalid | key=categories reason=invalid_or_missing action=default_applied")
        categories = DEFAULT_CONFIG["categories"]

    # Normalize empty categories explicitly (important for downstream safety)
    if len(categories) == 0:
        log_error("config_warning | reason=empty_categories action=fallback_active")

    config["categories"] = categories

    # -------------------------------------------------
    # FINAL GUARANTEE (SCHEMA ENFORCEMENT)
    # -------------------------------------------------
    # Ensures ALL required keys exist even if YAML is partial
    for key, value in DEFAULT_CONFIG.items():
        if key not in config or config[key] is None:
            config[key] = value

    return config


# -------------------------------------------------
# INTERNAL: Load raw YAML file
# -------------------------------------------------
def _load_yaml():
    """
    Loads and parses YAML config safely.
    """

    try:
        log_info(f"config_load_start | path={CONFIG_PATH}")

        with open(CONFIG_PATH, "r") as file:
            config = yaml.safe_load(file)

        log_info("config_load_success")

        return config

    except FileNotFoundError:
        log_error(f"config_load_failed | reason=file_not_found path={CONFIG_PATH}")
        return None

    except yaml.YAMLError as e:
        log_error(f"config_load_failed | reason=yaml_error", error=e)
        return None

    except Exception as e:
        log_error(f"config_load_failed | reason=unexpected_error", error=e)
        return None


# -------------------------------------------------
# PUBLIC: Get configuration
# -------------------------------------------------
def get_config():
    global _config_cache

    if _config_cache is not None:
        return _config_cache

    log_info("config_get_start")

    config = _load_yaml()

    if config is None:
        log_error("config_fallback_used | reason=load_failed")
        _config_cache = DEFAULT_CONFIG.copy()
        return _config_cache

    config = _validate_config(config)

    _config_cache = config

    log_info("config_get_complete")

    return _config_cache