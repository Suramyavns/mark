import os
import platform

def get_platform_config():
    os_name = platform.system().lower()
    
    # Base editors configuration
    config = {
        "vscode": {
            "name": "Visual Studio Code",
            "command": "code",
            "download_url": None,
            "installer_name": None,
            "possible_paths": []
        },
        "cursor": {
            "name": "Cursor",
            "command": "cursor",
            "download_url": None,
            "installer_name": None,
            "possible_paths": []
        },
        "antigravity": {
            "name": "Antigravity",
            "command": "antigravity",
            "download_url": "https://antigravity.google/download",
            "installer_name": "AntigravitySetup.bin",
            "possible_paths": []
        }
    }
    
    if os_name == "windows":
        config["vscode"].update({
            "download_url": "https://code.visualstudio.com/download",
            "installer_name": "VSCodeUserSetup.exe",
            "possible_paths": [
                os.path.expandvars(r"%LocalAppData%\Programs\Microsoft VS Code\bin\code.cmd"),
                os.path.expandvars(r"%ProgramFiles%\Microsoft VS Code\bin\code.cmd"),
            ]
        })
        config["cursor"].update({
            "download_url": "https://cursor.com/download",
            "installer_name": "CursorSetup.exe",
            "possible_paths": [
                os.path.expandvars(r"%LocalAppData%\Programs\cursor\resources\app\bin\cursor.cmd"),
                os.path.expandvars(r"%LocalAppData%\cursor\Cursor.exe"),
            ]
        })
    elif os_name == "darwin":  # macOS
        config["vscode"].update({
            "download_url": "https://code.visualstudio.com/download",
            "installer_name": "VSCode-darwin-universal.zip",
            "possible_paths": [
                "/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code",
                os.path.expanduser("~/Applications/Visual Studio Code.app/Contents/Resources/app/bin/code"),
            ]
        })
        config["cursor"].update({
            "download_url": "https://cursor.com/download",
            "installer_name": "Cursor.dmg",
            "possible_paths": [
                "/Applications/Cursor.app/Contents/Resources/app/bin/cursor",
                os.path.expanduser("~/Applications/Cursor.app/Contents/Resources/app/bin/cursor"),
            ]
        })
    else:  # linux
        config["vscode"].update({
            "download_url": "https://code.visualstudio.com/download",
            "installer_name": "code_amd64.deb",
            "possible_paths": [
                "/usr/bin/code",
                "/usr/local/bin/code",
                "/snap/bin/code",
            ]
        })
        config["cursor"].update({
            "download_url": "https://cursor.com/download",
            "installer_name": "cursor.AppImage",
            "possible_paths": [
                os.path.expanduser("~/bin/cursor"),
                "/usr/local/bin/cursor",
                "/usr/bin/cursor",
            ]
        })

    return config

EDITORS = get_platform_config()