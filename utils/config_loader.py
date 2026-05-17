# -------------------------------------------------
# IMPORTS
# -------------------------------------------------
# Import required libraries
import os
import yaml

# Import modules from the project
from utils.logger import log_info, log_error


# -------------------------------------------------
# CONFIG PATH
# -------------------------------------------------
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config.yaml")


# -------------------------------------------------
# CONFIG CACHE
# -------------------------------------------------
# In-memory cache to avoid repeated disk reads
_config_cache = None


# -------------------------------------------------
# INTERNAL: Basic config validation
# -------------------------------------------------
def _validate_config(config):
    """
    Performs lightweight validation of expected config structure.

    Ensures safe types for known configuration keys.
    Invalid values are replaced with predefined safe defaults.
    """

    if not isinstance(config, dict):
        return {}

    # Validate folder prefix (used for folder naming)
    if "folder_prefix" in config and not isinstance(config["folder_prefix"], str):
        log_error("config_invalid | key=folder_prefix type=string action=default_applied")
        config["folder_prefix"] = "smartorg"

    # Validate dry_run flag (controls execution mode)
    if "dry_run" in config and not isinstance(config["dry_run"], bool):
        log_error("config_invalid | key=dry_run type=bool action=default_applied")
        config["dry_run"] = False

    return config


# -------------------------------------------------
# INTERNAL: Load raw YAML file
# -------------------------------------------------
def _load_yaml():
    """
    Loads and parses the YAML configuration file.

    Returns:
        dict: Parsed configuration data
        None: If file cannot be loaded or is invalid
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
        log_error(f"config_load_failed | reason=yaml_error error={e}")
        return None

    except Exception as e:
        log_error(f"config_load_failed | reason=unexpected_error error={e}")
        return None


# -------------------------------------------------
# CONFIG SCHEMA (DOCUMENTATION)
# -------------------------------------------------
# Expected configuration structure (config.yaml):
#
# folder_prefix (str):
#     Prefix used for generated folders.
#     Example: "smartorg"
#
# dry_run (bool):
#     Controls execution mode globally.
#     - True  → simulate actions
#     - False → execute filesystem changes
#
# Notes:
# - CLI arguments override config values
# - Invalid types are automatically corrected in runtime
# - Missing keys fall back to safe defaults


# -------------------------------------------------
# PUBLIC: Get configuration (main entry point)
# -------------------------------------------------
def get_config():
    """
    Application configuration entry point.

    This is the single source of truth for accessing config values.
    Implements caching to avoid repeated disk I/O.
    """

    global _config_cache

    # If already loaded, return cached version
    if _config_cache is not None:
        return _config_cache

    # Otherwise load configuration from disk
    log_info("config_get_start")

    config = _load_yaml()

    # Handle failed load before validation
    if config is None:
        log_error("config_fallback_used | reason=load_failed")
        _config_cache = {}
        return _config_cache

    # Apply lightweight structural validation
    config = _validate_config(config)

    # Store validated config in cache
    _config_cache = config

    log_info("config_get_complete")

    return _config_cache