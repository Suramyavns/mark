import logging
import webbrowser

logger = logging.getLogger(__name__)

async def open_url(url: str):
    # webbrowser.open is non-blocking and uses the system default browser
    webbrowser.open(url)

    logger.info(f"Opened {url} in default browser")