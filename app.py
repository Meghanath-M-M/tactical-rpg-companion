# -*- coding: utf-8 -*-
import os
import base64
import sqlite3
import streamlit as st
import re
from openai import OpenAI
from dotenv import load_dotenv

# Load system environment keys
load_dotenv()

# ==========================================
# DATABASE LAYER (Agent Persistent Memory)
# ==========================================
DB_FILE = "agent_memory.db"


def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tactical_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            initial_plan TEXT,
            critique TEXT,
            final_strategy TEXT
        )
    """)
    conn.commit()
    conn.close()


def log_agent_session(initial, critique, final):
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tactical_logs (initial_plan, critique, final_strategy) VALUES (?, ?, ?)",
        (initial, critique, final),
    )
    conn.commit()
    conn.close()


def get_historical_logs():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT timestamp, final_strategy FROM tactical_logs ORDER BY id DESC LIMIT 3"
    )
    logs = cursor.fetchall()
    conn.close()
    return logs


init_db()


# ==========================================
# CORE AI AGENT ENGINE
# ==========================================
class RPGTacticalAgent:
    def __init__(self, uploaded_file, game_name, playstyle):
        self.uploaded_file = uploaded_file
        self.game_name = game_name
        self.playstyle = playstyle
        self.token = os.getenv("GITHUB_TOKEN")

        if not self.token:
            st.error(
                "❌ Missing GITHUB_TOKEN environment variable. Please check your .env file."
            )
            st.stop()

        self.client = OpenAI(
            base_url="https://models.inference.ai.azure.com",
            api_key=self.token,
        )
        self.model_name = "gpt-4o-mini"

    def get_base64_image(self):
        return base64.b64encode(self.uploaded_file.getvalue()).decode("utf-8")

    def execute_tactical_cycle(self):
        base64_img = self.get_base64_image()

        # Step 1: Draft Strategy (Sanitized for Azure Safety Filters)
        status = st.status(
            f"🥷 Step 1: Scouting {self.game_name} environment...", expanded=False
        )

        custom_prompt = (
            f"Analyze this screenshot from the video game '{self.game_name}'. "
            f"Draft a strategic gameplay guide to resolve this encounter using a '{self.playstyle}' approach. "
            f"Identify NPCs, environmental advantages, and suggest specific in-game mechanics or tools. "
            f"Keep the tone analytical and focused on game mechanics."
            f"Note: Avoid any content that could be flagged by Azure's safety filters. Focus on tactical analysis and gameplay strategy without referencing real-world violence or sensitive topics."
        )

        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert video game mechanics analyst.",
                },
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": custom_prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_img}"
                            },
                        },
                    ],
                },
            ],
        )
        initial_plan = response.choices[0].message.content
        status.update(
            label="🥷 Step 1: Initial Tactical Draft Completed!", state="complete"
        )

        # Step 2: Critic Reflection Loop
        status = st.status(
            "🔍 Step 2: Critic Agent searching for tactical vulnerabilities...",
            expanded=False,
        )
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are a Game Strategy Critic."},
                {
                    "role": "user",
                    "content": f"Review this gameplay strategy. Identify logical flaws based on game mechanics, environmental limitations, or pathing vulnerabilities.\n\nPlan:\n{initial_plan}",
                },
            ],
        )
        critique = response.choices[0].message.content
        status.update(label="🔍 Step 2: Critic Review Complete!", state="complete")

        # Step 3: Final Refinement
        status = st.status(
            "🎯 Step 3: Lead Guide Editor finalizing deployment orders...",
            expanded=False,
        )
        response = self.client.chat.completions.create(
            model=self.model_name,
            messages=[
                {"role": "system", "content": "You are the Lead Guide Editor."},
                {
                    "role": "user",
                    "content": f"Rewrite the gameplay guide to eliminate all flaws identified by the critic. Format with clean bold headers and emojis.\n\nOriginal Plan:\n{initial_plan}\n\nCritic Feedback:\n{critique}",
                },
            ],
        )
        final_strategy = response.choices[0].message.content
        status.update(
            label="🎯 Step 3: Deployment Strategy Formulated!", state="complete"
        )

        log_agent_session(initial_plan, critique, final_strategy)

        return initial_plan, critique, final_strategy


def clean_text_for_speech(text):
    """
    Removes Markdown formatting symbols (#, *, _, `, etc.)
    to make text friendly for Text-to-Speech engines.
    """
    if not text:
        return ""

    # 1. Remove Headers (e.g., ### Overview -> Overview)
    text = re.sub(re.compile(r"^#+\s*", re.MULTILINE), "", text)

    # 2. Remove Bold/Italic formatting asterisks and underscores (e.g., **Bold** -> Bold)
    text = text.replace("***", "").replace("**", "").replace("*", "")
    text = text.replace("___", "").replace("__", "").replace("_", "")

    # 3. Remove backticks/code block symbols (e.g., `code` -> code)
    text = text.replace("`", "")

    # 4. Clean up any accidental double spaces caused by formatting removal
    text = re.sub(r" +", " ", text)

    return text.strip()


# ==========================================
# STREAMLIT UI DESIGN (UI/UX Layer)
# ==========================================
st.set_page_config(page_title="Tactical RPG Agent", layout="wide", page_icon="🛡️")

st.title("🛡️ Tactical RPG Multi-Agent Companion")
st.caption(
    "Powered by GitHub Models (GPT-4o) & SQLite Memory Layer | Creative Apps Track"
)

# SIDEBAR: Settings & Memory
with st.sidebar:
    st.header("⚙️ Tactical Settings")
    selected_game = st.text_input("Game Title", value="Ghost of Tsushima")
    selected_playstyle = st.selectbox(
        "Preferred Playstyle",
        [
            "Stealth (Covert, Silenced, Assassinations)",
            "Aggressive (Direct Assault, Heavy Melee/Firepower)",
            "Ranged (Sniper, Bows, Distance Tactics)",
            "Environmental (Traps, Explosives, Sabotage)",
        ],
    )

    st.divider()

    st.header("📁 Agent Memory Logs")
    past_sessions = get_historical_logs()
    if past_sessions:
        for timestamp, strategy in past_sessions:
            with st.expander(f"🕒 Record: {timestamp[:16]}"):
                st.markdown(strategy[:200] + "...")
    else:
        st.write("No historical data recorded in memory yet.")

# MAIN INTERFACE
col1, col2 = st.columns([1, 1.5])

with col1:
    st.header("🎮 Capture Intake")
    uploaded_file = st.file_uploader(
        "Upload a live gameplay screenshot", type=["jpg", "jpeg", "png"]
    )

    if uploaded_file:
        st.image(
            uploaded_file,
            caption="Live Game State Visual Feed",
            use_container_width=True,
        )
        generate_btn = st.button("🚀 Trigger Autonomous Reasoning Loop", type="primary")

with col2:
    st.header("🧠 Agent Reasoning Dashboard")

    if uploaded_file and "generate_btn" in locals() and generate_btn:
        # Pass the new settings into the agent!
        agent = RPGTacticalAgent(uploaded_file, selected_game, selected_playstyle)

        initial, critique, final = agent.execute_tactical_cycle()

        tab1, tab2, tab3 = st.tabs(
            ["🎯 Final Blueprint", "🔍 Critic Reflection Log", "🧠 Original Draft"]
        )

        with tab1:
            st.markdown(final)
        with tab2:
            st.info(critique)
        with tab3:
            st.text_area("Raw Initial Plan", initial, height=300)
        # Generate Audio Briefing (Cross-platform TTS)
        st.divider()
        st.subheader("🎧 Audio Tactical Briefing")
        with st.spinner("Compiling voice transmission..."):
            try:
                import asyncio
                import edge_tts

                # Clean the text of emojis
                clean_text = clean_text_for_speech(final)
                clean_text = clean_text.encode("ascii", "ignore").decode("ascii")

                # Use edge-tts (cross-platform, free)
                async def generate_audio():
                    communicate = edge_tts.Communicate(clean_text, "en-US-AriaNeural")
                    await communicate.save("briefing.mp3")

                asyncio.run(generate_audio())
                st.audio("briefing.mp3", format="audio/mp3")
            except Exception as e:
                st.warning(f"Audio module offline: {e}")
    elif not uploaded_file:
        st.info(
            "Upload a live gameplay snapshot on the left to activate the Multi-Agent Thinking loop."
        )
