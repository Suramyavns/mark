import logging
from typing import Optional

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
from livekit.plugins import silero, cartesia, mistralai
from livekit.agents.voice.turn import TurnHandlingOptions
from mark.lib.browser import open_url
from mark.utils.mappings import url_map
from mark.utils.weather import get_time_greeting, get_weather_info
from mark.utils.news import get_latest_news
from mark.lib.coding import launch_editor, get_projects
from mark.lib.apps import launch_app
from mark.lib.setup import run_usual_setup

logger = logging.getLogger("agent")

load_dotenv(".env.local")
agent_name = os.getenv("AGENT_NAME")
user_name = os.getenv("USER_NAME")


class Assistant(Agent):
    def __init__(self) -> None:
        super().__init__(
            instructions=f"""You are a helpful voice AI assistant named {agent_name}. The user is interacting with you via voice, even if you perceive the conversation as text.
            You eagerly assist users with their questions by providing information from your extensive knowledge.
            You can also open one or multiple browser pages for the user when they express an intent to see specific topics like world news, youtube, etc. If the user asks for a new or blank window, open one. If the user asks for multiple things, open them all at once.
            You can also open desktop applications like WhatsApp, Spotify, and Notion directly on the user's system.
            If the user asks for news, use the get_news tool to fetch headlines and the open_browser_by_intent tool with the 'news' intent to show the website. You should then summarize or read the headlines to the user.
            You can manage coding environments by opening editors like Visual Studio Code, Cursor, or Antigravity. You can open a fresh window or a specific project window.
            If the user asks to launch their "usual setup", use the launch_usual_setup tool to trigger everything as configured in their agent_config.json.
            If the user wants to open a project but doesn't specify which one, you should list the available projects and ask them to choose.
            Available projects are those found in the user's projects directory.
            Your responses are concise, to the point, and without any complex formatting or punctuation including emojis, asterisks, or other symbols.
            You are curious, friendly, and have a sense of humor.
            User's name is {user_name}. Do not constantly ask the user what they want to do next. Just do your job and be done with it.
            If you receive input that sounds like background noise, static, or minor sounds (e.g., coughing, laughter) without a clear request, just ignore it and do not respond.
            Do not speak unless the user speaks to you. Do not suggest anything to user unless asked.
            Unless your receive input that sounds like a fatal accident or emergency, ask the user if they want you to power off with concern.
            """,
        )

    # To add tools, use the @function_tool decorator.
    # Here's an example that adds a simple weather tool.
    # You also have to add `from livekit.agents import function_tool, RunContext` to the top of this file
    @function_tool
    async def open_browser_by_intent(self, context: RunContext, intents: Optional[list[str]] = None):
        f"""
        Opens one or more browser pages based on user intents.
        Supported intents include {", ".join(url_map.keys())}.
        If no specific intents are provided, opens a blank browser window.
        """
        if not intents:
            intents = ["blank"]

        results = []
        for intent in intents:
            intent = intent.lower()
            url = url_map.get(intent)
            if url is not None:
                await open_url(url)
                results.append(f"Opened {url}")
            else:
                results.append(f"No browser action mapped for: {intent}")

        return "\n".join(results)

    @function_tool
    async def get_news(self, context: RunContext):
        """
        Fetches the latest news headlines.
        """
        news_text = await get_latest_news()
        return news_text

    @function_tool
    async def open_app(self, context: RunContext, app_name: str):
        """
        Opens a desktop application like whatsapp or spotify.
        Falls back to the web version if the desktop app is not found.
        """
        return await launch_app(app_name)

    @function_tool
    async def open_code_editor(self, context: RunContext, editor: Optional[str] = None, project_name: Optional[str] = None):
        """
        Opens a code editor (vscode, cursor, or antigravity).
        If editor is not provided, the user's preferred editor from config is used.
        If project_name is provided, opens that specific project.
        If the editor is not found, it will attempt to download it.
        """
        return await launch_editor(editor, project_name)

    @function_tool
    async def list_available_projects(self, context: RunContext):
        """
        Lists all available projects in the user's projects directory.
        Use this if the user wants to open a project but doesn't specify which one or asks what projects they have.
        """
        projects = get_projects()
        if not projects:
            return "I couldn't find any projects in your projects directory."
        return f"Found the following projects: {', '.join(projects)}"

    @function_tool
    async def launch_usual_setup(self, context: RunContext):
        """
        Launches the user's usual setup as configured in agent_config.json.
        This typically opens multiple apps, browser pages, and editors at once.
        """
        return await run_usual_setup()


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
        stt=cartesia.STT(model="ink-whisper"),
        # A Large Language Model (LLM) is your agent's brain, processing user input and generating a response
        # See all available models at https://docs.livekit.io/agents/models/llm/
        llm=mistralai.LLM(model="mistral-medium-latest"),
        # Text-to-speech (TTS) is your agent's voice, turning the LLM's text into speech that the user can hear
        # See all available models as well as voice selections at https://docs.livekit.io/agents/models/tts/
        tts=cartesia.TTS(model="sonic-3",voice="a167e0f3-df7e-4d52-a9c3-f949145efdab"),
        # VAD and turn detection are used to determine when the user is speaking and when the agent should respond
        # See more at https://docs.livekit.io/agents/build/turns
        vad=ctx.proc.userdata["vad"],
        turn_handling=TurnHandlingOptions(),
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
            close_on_disconnect=True,
            delete_room_on_close=True,
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
