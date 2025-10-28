import os
import yaml
import copy
from pathlib import Path
from omegaconf import OmegaConf


CONFIG_YAML = "config.yaml"
USER_YAML = "user.yaml"


def load_yaml(path: str):
    if not os.path.exists(path):
        return {}
    with open(path, "r") as f:
        return yaml.safe_load(f) or {}


def deep_merge(base: dict, overrides: dict) -> dict:
    """Recursively merge overrides into base (in place)."""
    for k, v in overrides.items():
        if isinstance(base.get(k), dict) and isinstance(v, dict):
            deep_merge(base[k], v)
        else:
            base[k] = copy.deepcopy(v)
    return base


def get_config_path():
    config_dir = os.path.join(os.path.dirname(__file__), "..", "configs")
    config_dir = os.path.abspath(config_dir)
    return os.path.join(config_dir, CONFIG_YAML)


def get_user_config_path():
    config_dir = Path.home() / ".nora"
    config_dir.mkdir(exist_ok=True)
    return config_dir / USER_YAML


def configure_user_config():
    """Interactively create ~/.nora/user.yaml with user API keys.
    """
    config_path = get_user_config_path()
    print(f"Let's configure your NoRA keys:\n")

    notion_token = input("Enter your Notion integration token: ")
    notion_papers_db_id = input("Enter your Notion Papers database ID: ")
    notion_people_db_id = input("Enter your Notion People database ID: ")
    notion_affiliations_db_id = input("Enter your Notion Affiliations database ID: ")
    notion_venues_db_id = input("Enter your Notion Venues database ID: ")
    notion_topics_db_id = input("Enter your Notion Topics database ID: ")

    zotero_library_id = input("Enter your Zotero library ID (optional): ")
    zotero_api_token = input("Enter your Zotero API token (optional): ")

    user_cfg = {
        "notion": {
            "token": notion_token,
            "papers_db_id": notion_papers_db_id,
            "people_db_id": notion_people_db_id,
            "affiliations_db_id": notion_affiliations_db_id,
            "venues_db_id": notion_venues_db_id,
            "topics_db_id": notion_topics_db_id,
        },
        "zotero": {
            "library_id": zotero_library_id,
            "api_token": zotero_api_token,
        },
    }

    with open(config_path, "w") as f:
        yaml.dump(user_cfg, f)

    # Load the user-specific config along with static config it not
    # overwritten by the user config. Then save all into the new user
    # config file. This allows exposing explicitly in the user's config
    # all the configuration variables, while preserving any
    # already-defined keys before this configuration call
    cfg_full = OmegaConf.to_container(load_config(), resolve=True)
    with open(config_path, "w") as f:
        yaml.dump(cfg_full, f)

    print(f"✅ Configuration saved to {config_path}")


def load_user_config(depth: int=0):
    """Load user keys from ~/.nora/user.yaml"""
    config_path = get_user_config_path()
    if config_path.exists():
        return load_yaml(config_path)
    elif depth < 1:
        configure_user_config()
        return load_user_config(depth=1)
    else:
        print(f"⚠️ No {USER_YAML} file found. Run `nora configure` first.")
        raise SystemExit(1)


def load_config():
    """
    Loads NoRA configuration by merging:
      1. Static defaults from src/nora/configs/config.yaml
      2. User-specific overrides from ~/.nora/user.yaml
    """
    # Find base config directory (relative to installed package).
    # Normally this call could be bypassed if configure_user_config()
    # was properly called. But this allows for making up for users
    # potentially tampering with their private config file and deleting
    # essential keys
    cfg = load_yaml(get_config_path())

    # Get config holding user keys
    user_cfg = load_user_config()
    if user_cfg:
        for k, v in user_cfg.items():
            if k in cfg and isinstance(v, dict):
                deep_merge(cfg[k], v)
            else:
                cfg[k] = v

    return OmegaConf.create(cfg)
