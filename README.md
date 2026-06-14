# 🛡️ Tactical RPG Multi-Agent Companion
**Agents League Hackathon | Creative Apps Track**
🚀 **[CLICK HERE TO LAUNCH THE LIVE DEMO](https://tactical-rpg-agent.streamlit.app/)** 🚀

An interactive, multi-modal AI commander that analyzes live gameplay screenshots and provides real-time tactical advice using simulated enterprise knowledge retrieval and multi-agent reasoning.

## 🚀 The Vision
The Tactical RPG Multi-Agent Companion transforms static game guides into an interactive, real-time esports coach. By uploading a screenshot of a complex gameplay scenario, users trigger an autonomous AI reasoning loop that drafts, critiques, and finalizes a personalized battle strategy. 

## 🏗️ Architectural Proof of Concept (Microsoft IQ)
To ensure zero-latency for gamers while satisfying strict enterprise data grounding requirements, this project utilizes a localized Architectural Proof of Concept:
* **Foundry IQ Simulation:** Uses a deterministic SQLite database to retrieve verified gaming mechanics and lore, grounding the LLM and preventing hallucinations. This mirrors the exact data structure of a production Azure AI Search vector database.
* **Work IQ Simulation:** Maintains persistent memory of past tactical encounters, allowing the agent to learn and adapt its strategies over time based on the user's specific playstyle.

## ✨ Key Features
* **Multi-Agent Reasoning Loop:** Every screenshot passes through a Planner Agent, a Critic Agent (for pathing/mechanics flaw detection), and a Lead Editor for final sanitization.
* **Live Tactical Comms:** A dynamic chat interface allowing users to ask specific questions about their current visual environment.
* **Voice-Activated Briefings:** Integrates Edge-TTS to read out tactical responses in character (e.g., Cyberpunk Mercenary, Analytical Commander).
* **1-Click Export:** Instantly download your customized tactical blueprint as a markdown file.

## 💻 Tech Stack
* **Frontend:** Streamlit
* **AI/LLM:** GitHub Models Inference API (`gpt-4o-mini`)
* **Database:** SQLite (Memory & Enterprise Knowledge Graph)
* **Audio:** `edge-tts` / `asyncio`
* **Language:** Python 3.11+

## 🛠️ How to Run Locally

1. **Clone the repository:**
   ```bash
   git clone [https://github.com/yourusername/tactical-rpg-companion.git](https://github.com/yourusername/tactical-rpg-companion.git)
   cd tactical-rpg-companion
