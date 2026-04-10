import os
import logging
from mark.lib.browser import open_url
from mark.utils.apps import APP_CONFIG

logger = logging.getLogger(__name__)

def is_app_installed(app_name: str) -> bool:
    """Checks if a desktop app is installed on the system."""
    config = APP_CONFIG.get(app_name.lower())
    if not config:
        return False
    
    if os.name == "nt": # Windows
        return any(os.path.exists(p) for p in config["windows_paths"])
    
    # Expand for macOS/Linux if needed
    return False

async def launch_app(app_name: str) -> str:
    """Launches a desktop app or falls back to web version."""
    name = app_name.lower()
    config = APP_CONFIG.get(name)
    
    if not config:
        return f"I don't have a configuration for the {app_name} app."

    if is_app_installed(name):
        await open_url(config["uri"])
        return f"Opening {app_name} desktop app."
    else:
        await open_url(config["web"])
        return f"{app_name} desktop app not found. Opening the web version instead."
