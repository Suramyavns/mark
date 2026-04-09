import logging

from dotenv import load_dotenv
from livekit import rtc
from livekit.agents import function_tool, RunContext
from livekit.agents import (
    Agent,
    AgentServer,
    AgentSession,
    JobContext,
    JobProcess,
    cli,
    inference,
    room_io,
)
import os
from livekit.plugins import ai_coustics, noise_cancellation, silero
from mark.lib.browser import open_url
from mark.utils.mappings import url_map
from mark.utils.weather import get_time_greeting, get_weather_info
from mark.utils.news import get_latest_news

logger = logging.getLogger("agent")

load_dotenv(".env.local")
agent_name = os.getenv("AGENT_NAME")
user_name = os.getenv("USER_NAME")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=f"""You are a helpful voice AI assistant named {agent_name}. The user is interacting with you via voice, even if you perceive the conversation as text.
            You eagerly assist users with their questions by providing information from your extensive knowledge.
            You can also open one or multiple browser pages for the user when they express an intent to see specific topics like world news, youtube, etc. If the user asks for multiple things, open them all at once.
            If the user asks for news, use the get_news tool to fetch headlines and open the news website. You should then summarize or read the headlines to the user.
            Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
            You are curious, friendly, and have a sense of humor.
            User's name is {user_name}. Do not constantly ask the user what they want to do next. Just do your job and be done with it.
            If you receive input that sounds like background noise, static, or minor sounds (e.g., coughing, laughter) without a clear request, just ignore it and do not respond.
            Unless your receive input that sounds like a fatal accident or emergency, ask the user if they want you to power off with concern.
            """,
        )

    # To add tools, use the @function_tool decorator.
    # Here's an example that adds a simple weather tool.
    # You also have to add `from livekit.agents import function_tool, RunContext` to the top of this file
    @function_tool
    async def open_browser_by_intent(self, context: RunContext, intents: list[str]):
        f"""
        Opens one or more browser pages based on user intents.
        Supported intents include {", ".join(url_map.keys())}.
        """
        results = []
        for intent in intents:
            intent = intent.lower()
            url = url_map.get(intent)
            if url:
                await open_url(url)
                results.append(f"Opened {url}")
            else:
                results.append(f"No browser action mapped for: {intent}")

        return "\n".join(results)

    @function_tool
    async def get_news(self, context: RunContext):
        """
        Fetches the latest news headlines and opens the news browser page.
        """
        news_text = await get_latest_news()
        # Open news website as well
        await open_url(url_map.get("news", "https://worldmonitor.app"))
        return news_text


server = AgentServer()


def prewarm(proc: JobProcess):
    proc.userdata["vad"] = silero.VAD.load()


server.setup_fnc = prewarm


@server.rtc_session(agent_name=agent_name)
async def my_agent(ctx: JobContext):
    # Logging setup
    # Add any other context you want in all log entries here
    ctx.log_context_fields = {
        "room": ctx.room.name,
    }

    # Set up a voice AI pipeline using OpenAI, Cartesia, Deepgram, and the LiveKit turn detector
    session = AgentSession(
        # Speech-to-text (STT) is your agent's ears, turning the user's speech into text that the LLM can understand
        # See all available models at https://docs.livekit.io/agents/models/stt/
        stt=inference.STT(model="elevenlabs/scribe_v2_realtime", language="en"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=inference.LLM(model="openai/gpt-5.2-chat-latest"),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=inference.TTS(model="cartesia/sonic-3"),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        vad=ctx.proc.userdata["vad"],
        turn_detection="stt",
        # allow the LLM to generate a response while waiting for the end of turn
        # See more at https://docs.livekit.io/agents/build/audio/#preemptive-generation
        preemptive_generation=True,
    )

    # Start the session, which initializes the voice pipeline and warms up the models
    await session.start(
        agent=Assistant(),
        room=ctx.room,
        room_options=room_io.RoomOptions(
            audio_input=room_io.AudioInputOptions(
                noise_cancellation=lambda params: (
                    noise_cancellation.BVCTelephony()
                    if params.participant.kind
                    == rtc.ParticipantKind.PARTICIPANT_KIND_SIP
                    else ai_coustics.audio_enhancement(
                        model=ai_coustics.EnhancerModel.QUAIL_VF_L
                    )
                ),
            ),
        ),
    )

    # Join the room and connect to the user
    await ctx.connect()

    # Greeting with time and weather
    greeting = get_time_greeting()
    city, weather = await get_weather_info()
    await session.say(
        f"{greeting}! It's {weather} in {city}. I'm {agent_name}, how can I help you today?",
        allow_interruptions=True,
    )


if __name__ == "__main__":
    cli.run_app(server)
