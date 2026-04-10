import os
from mark.utils.mappings import url_map

APP_CONFIG = {
    "whatsapp": {
        "uri": "whatsapp://",
        "web": url_map.get("whatsapp", "https://web.whatsapp.com"),
        "windows_paths": [
            os.path.expandvars(r"%AppData%\Whatsapp\Whatsapp.exe"),
            os.path.expandvars(r"%LocalAppData%\WhatsApp\WhatsApp.exe"),
            os.path.expandvars(r"%LocalAppData%\Microsoft\WindowsApps\WhatsApp.exe"),
            os.path.expandvars(r"%LocalAppData%\Packages\5319275A.WhatsAppDesktop_cv1g1gvanyjgm"),
        ]
    },
    "spotify": {
        "uri": "spotify:",  
        "web": url_map.get("spotify", "https://open.spotify.com"),
        "windows_paths": [
            os.path.expandvars(r"%AppData%\Spotify\Spotify.exe"),
            os.path.expandvars(r"%LocalAppData%\Microsoft\WindowsApps\Spotify.exe"),
            os.path.expandvars(r"%LocalAppData%\Spotify\Spotify.exe"),
        ]
    },
    "notion": {
        "uri": "notion://",
        "web": url_map.get("notion", "https://notion.so"),
        "windows_paths": [
            os.path.expandvars(r"%LocalAppData%\Programs\Notion\Notion.exe"),
            os.path.expandvars(r"%LocalAppData%\Notion\Notion.exe"),
        ]
    }
}