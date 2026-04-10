import os
import json
import logging

logger = logging.getLogger(__name__)

def load_config():
    # Possible locations for the config file
    possible_paths = [
        "agent_config.json",  # Root of project if started from there
        "server/agent_config.json",  # Root of workspace if started from there
        os.path.join(os.path.dirname(__file__), "..", "..", "..", "..", "agent_config.json"), # Relative to this file
        os.path.abspath(os.path.join(os.getcwd(), "agent_config.json"))
    ]

    for path in possible_paths:
        if os.path.exists(path):
            try:
                with open(path, "r") as f:
                    logger.info(f"Loading config from {os.path.abspath(path)}")
                    return json.load(f)
            except Exception as e:
                logger.error(f"Error loading config from {path}: {e}")
    
    logger.warning("No agent_config.json found, using defaults.")
    return {}