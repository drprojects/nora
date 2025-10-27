import os
import yaml
import copy
from pathlib import Path
from omegaconf import OmegaConf


def load_yaml(path):
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
    return os.path.join(config_dir, "config.yaml")


def get_private_config_path():
    config_dir = Path.home() / ".nora"
    config_dir.mkdir(exist_ok=True)
    return config_dir / "config.yaml"


def configure_private_config():
    """Interactively create ~/.nora/config.yaml with user API keys.
    """
    config_path = get_private_config_path()
    print("Let's configure your NoRA keys (saved in ~/.nora/config.yaml):\n")

    notion_token = input("Enter your Notion integration token: ")
    notion_papers_db_id = input("Enter your Notion Papers database ID: ")
    notion_people_db_id = input("Enter your Notion People database ID: ")
    notion_affiliations_db_id = input("Enter your Notion Affiliations database ID: ")
    notion_venues_db_id = input("Enter your Notion Venues database ID: ")
    notion_topics_db_id = input("Enter your Notion Topics database ID: ")

    zotero_library_id = input("Enter your Zotero library ID (optional): ")
    zotero_api_token = input("Enter your Zotero API token (optional): ")

    cfg = {
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
        yaml.dump(cfg, f)

    print(f"✅ Configuration saved to {config_path}")


def load_private_config(depth=0):
    """Load private keys from ~/.nora/config.yaml"""
    config_path = get_private_config_path()
    if config_path.exists():
        return load_yaml(config_path)
    elif depth < 1:
        configure_private_config()
        return load_private_config(depth=1)
    else:
        print("⚠️ No ~/.nora/config.yaml file found. Run `nora configure` first.")
        raise SystemExit(1)


def load_config():
    """
    Loads NoRA configuration by merging:
      1. Static defaults from src/nora/configs/
      2. User-specific overrides from ~/.nora/config.yaml
    """
    # Find base config directory (relative to installed package)
    cfg = load_yaml(get_config_path())

    # Get user config holding private keys
    user_cfg = load_private_config()
    if user_cfg:
        for k, v in user_cfg.items():
            if k in cfg:
                deep_merge(cfg[k], v)
            else:
                cfg[k] = v

    return OmegaConf.create(cfg)
