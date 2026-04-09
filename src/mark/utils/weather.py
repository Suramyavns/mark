import aiohttp
import logging
from datetime import datetime
import os
from dotenv import load_dotenv

load_dotenv(".env.local")

logger = logging.getLogger(__name__)

user_name = os.getenv("USER_NAME")

async def get_weather_info():
    try:
        async with aiohttp.ClientSession() as session:
            # 1. Get location via IP
            async with session.get("https://ipapi.co/json/") as resp:
                if resp.status != 200:
                    return "unknown location", "unknown weather"
                loc_data = await resp.json()
                city = loc_data.get("city", "San Francisco")
                lat = loc_data.get("latitude", 37.7749)
                lon = loc_data.get("longitude", -122.4194)

            # 2. Get weather for that location
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            async with session.get(weather_url) as resp:
                if resp.status != 200:
                    return city, "unknown weather"
                weather_data = await resp.json()
                temp = weather_data["current_weather"]["temperature"]
                # Map weather codes to strings if desired, but just temp is often enough for a greeting
                return city, f"{temp}°C"
    except Exception as e:
        logger.error(f"Error fetching weather: {e}")
        return "your location", "the current weather"

def get_time_greeting():
    hour = datetime.now().hour
    if hour < 12:
        return f"Good morning {user_name}"
    elif hour < 17:
        return f"Good afternoon {user_name}"
    elif hour < 5:
        return f"Good morning {user_name}, it's dark outside."
    else:
        return f"Good evening {user_name}"
