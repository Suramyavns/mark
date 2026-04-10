import os
import subprocess
import shutil
import logging
import json
from typing import Optional, List
from mark.utils.config import load_config
from mark.utils.editors import EDITORS
from mark.lib.browser import open_url

logger = logging.getLogger(__name__)

config = load_config()
PROJECTS_ROOT = config.get("project_root")
PREFERRED_EDITOR = config.get("preferred_editor")

def get_projects() -> List[str]:
    """Returns a list of project directories in the projects root."""
    try:
        if not os.path.exists(PROJECTS_ROOT):
            return []
        return [d for d in os.listdir(PROJECTS_ROOT) if os.path.isdir(os.path.join(PROJECTS_ROOT, d))]
    except Exception as e:
        logger.error(f"Error listing projects: {e}")
        return []

def find_editor_path(name: str) -> Optional[str]:
    """Finds the executable path for a given editor."""
    editor = EDITORS.get(name.lower())
    if not editor:
        return None
    
    # 1. Check if it's in PATH
    path = shutil.which(editor["command"])
    if path:
        return path
    
    # 2. Check common installation paths
    for p in editor["possible_paths"]:
        if os.path.exists(p):
            return p
            
    return None

async def launch_editor(name: Optional[str] = None, project_name: Optional[str] = None) -> str:
    """Launches the editor, optionally with a project."""
    if not name:
        name = PREFERRED_EDITOR
    
    path = find_editor_path(name)
    
    if not path:
        editor_info = EDITORS.get(name.lower())
        url = editor_info.get("download_url") if editor_info else None
        if url:
            await open_url(url)
            return f"I couldn't find {name} installed on your system. I've opened the download page for you in your browser."
        return f"I couldn't find {name} installed on your system, and I don't have a download URL for it."

    cmd = [path]
    if project_name:
        project_path = os.path.join(PROJECTS_ROOT, project_name)
        if os.path.exists(project_path):
            cmd.append(project_path)
            message = f"Opening {project_name} in {EDITORS[name.lower()]['name']}."
        else:
            message = f"Project {project_name} not found. Opening a fresh {EDITORS[name.lower()]['name']} window."
    else:
        message = f"Opening a fresh {EDITORS[name.lower()]['name']} window."

    try:
        subprocess.Popen(cmd, shell=True)
        return message
    except Exception as e:
        logger.error(f"Error launching {name}: {e}")
        return f"Failed to launch {name}: {str(e)}"
