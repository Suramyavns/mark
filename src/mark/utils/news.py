import httpx
import logging

logger = logging.getLogger(__name__)


async def get_latest_news() -> str:
    """
    Fetches latest world news headlines from a public API.
    """
    url = "https://ok.surf/api/v1/cors/news-feed"
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url)
            response.raise_for_status()
            data = response.json()

            # The API returns news by category. Let's take 'World' or 'US'
            news_items = data.get("World", [])[:5]  # Get top 5 world news
            if not news_items:
                news_items = data.get("US", [])[:5]

            headlines = []
            for item in news_items:
                title = item.get("title")
                source = item.get("source")
                if title:
                    headlines.append(f"{title}, from {source}.")

            if not headlines:
                return "I couldn't find any news headlines right now."

            return "Here are the latest headlines:\n" + "\n".join(headlines)
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
        return "I'm sorry, I'm having trouble fetching the news right now."
