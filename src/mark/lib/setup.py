import logging
from mark.utils.config import load_config
from mark.lib.apps import launch_app
from mark.lib.coding import launch_editor
from mark.lib.browser import open_url
from mark.utils.mappings import url_map
from mark.utils.editors import EDITORS

logger = logging.getLogger(__name__)

async def run_usual_setup():
    """Parses and executes the usual_setup from config."""
    config = load_config()
    setup_str = config.get("usual_setup", "")
    if not setup_str:
        return "No usual setup configured in agent_config.json."

    # Remove the word 'open ' if present and split by commas
    items = [item.strip().lower() for item in setup_str.replace("open ", "").split(",")]
    
    results = []
    for item in items:
        # Priority 1: Check if it's one of our defined editors
        if item in EDITORS:
            res = await launch_editor(item)
            results.append(res)
            continue

        # Priority 2: Check if it's one of our desktop apps
        if item in ["whatsapp", "spotify", "notion"]:
            res = await launch_app(item)
            results.append(res)
            continue
            
        # Priority 3: Check browser mappings
        if item in url_map:
            await open_url(url_map[item])
            results.append(f"Opened {item} in browser.")
            continue
            
        results.append(f"Could not find an action for: {item}")

    return "Usual setup triggered. Everything is opening up for you."
