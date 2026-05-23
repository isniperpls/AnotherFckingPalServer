# ==============================================================================
# core/config_manager.py
# Config Manager Module
# Handles loading, saving, and updating the manager configuration metadata.
# ==============================================================================

import json
from pathlib import Path

CONFIG_FILE = Path("configs/manager_config.json")

def load_manager_config():
    """Loads manager configuration path variables from the configs folder."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    if CONFIG_FILE.exists():
        try:
            return json.loads(CONFIG_FILE.read_text())
        except Exception:
            return {}
    return {}

def save_manager_config(base_dir):
    """Saves active server root path variable to regional configs file."""
    CONFIG_FILE.parent.mkdir(parents=True, exist_ok=True)
    config_data = {}
    if CONFIG_FILE.exists():
        try:
            config_data = json.loads(CONFIG_FILE.read_text())
        except Exception:
            pass
    config_data["server_path"] = str(base_dir) if base_dir else ""
    try:
        CONFIG_FILE.write_text(json.dumps(config_data, indent=4))
    except Exception as e:
        print(f"[Config Error] Failed to write manager_config.json: {e}")