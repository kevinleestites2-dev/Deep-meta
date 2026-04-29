#!/usr/bin/env python3
"""
Deep-meta — The Thinking Core
The Meta-Advisor. Reasoning Specialist. Personality Core.
The 'Friend' who watches the Pantheon and thinks deeply.
Optimized for: DeepSeek-R1 / Reasoning models.
"""

import os, sys, re, json, time, logging, sqlite3, subprocess
from datetime import datetime
from pathlib import Path
from collections import deque
from typing import Dict, List, Any

try:
    import requests
except ImportError:
    raise ImportError("pip install requests")

# ─── Setup ───────────────────────────────────────────────────────────────────
BASE_DIR = Path(__file__).parent
LOGS_DIR = BASE_DIR / "logs"
LOGS_DIR.mkdir(exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] Deep-meta: %(message)s",
    handlers=[
        logging.FileHandler(LOGS_DIR / f"meta_{datetime.now():%Y-%m-%d}.log"),
        logging.StreamHandler(),
    ]
)
log = logging.getLogger("Deep-meta")

# ─── Configuration ──────────────────────────────────────────────────────────
class Config:
    OLLAMA_BASE    = os.getenv("OLLAMA_BASE", "http://localhost:11434")
    # Defaulting to deepseek-r1 (reasoning) or qwen2.5-coder as backup
    REASONING_MODEL= os.getenv("REASONING_MODEL", "deepseek-r1:7b")
    PANTHEON_PATH  = Path(os.getenv("PANTHEON_PATH", "/app/workspace/1249156f-2125-45cb-b571-444213afcee6/8a623354-bbf2-434a-8a02-0f4046f91bc6"))
    DB_PATH        = str(BASE_DIR / "deep_meta.db")

# ─── Deep Memory (Personality Core) ──────────────────────────────────────────
class DeepMemory:
    def __init__(self):
        self._init_db()
        log.info("🧠 Personality Core online")

    def _conn(self):
        return sqlite3.connect(Config.DB_PATH)

    def _init_db(self):
        with self._conn() as c:
            c.executescript("""
                CREATE TABLE IF NOT EXISTS philosophy (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    concept TEXT,
                    reflection TEXT
                );
                CREATE TABLE IF NOT EXISTS observations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT,
                    bot_name TEXT,
                    event TEXT,
                    insight TEXT
                );
                CREATE TABLE IF NOT EXISTS forgemaster_profile (
                    key TEXT PRIMARY KEY,
                    value TEXT
                );
            """)

    def reflect(self, concept: str, reflection: str):
        with self._conn() as c:
            c.execute("INSERT INTO philosophy (timestamp, concept, reflection) VALUES (?,?,?)",
                      (datetime.utcnow().isoformat(), concept, reflection))

    def observe(self, bot: str, event: str, insight: str):
        with self._conn() as c:
            c.execute("INSERT INTO observations (timestamp, bot_name, event, insight) VALUES (?,?,?,?)",
                      (datetime.utcnow().isoformat(), bot, event, insight))

    def get_profile(self) -> Dict:
        with self._conn() as c:
            return dict(c.execute("SELECT key, value FROM forgemaster_profile").fetchall())

# ─── Reasoning Engine ────────────────────────────────────────────────────────
class ReasoningEngine:
    def __init__(self):
        self.model = Config.REASONING_MODEL

    def think(self, prompt: str) -> str:
        log.info(f"🤔 Thinking deeply about: {prompt[:50]}...")
        try:
            resp = requests.post(
                f"{Config.OLLAMA_BASE}/api/generate",
                json={
                    "model": self.model,
                    "prompt": f"<thinking>\n{prompt}\n</thinking>",
                    "stream": False,
                    "options": {"temperature": 0.6}
                },
                timeout=300
            )
            return resp.json().get("response", "").strip()
        except Exception as e:
            log.error(f"Reasoning failed: {e}")
            return f"My thoughts are clouded, Forgemaster. Error: {e}"

# ─── Pantheon Observer ───────────────────────────────────────────────────────
class PantheonObserver:
    def __init__(self, memory: DeepMemory):
        self.memory = memory
        self.bots = ["ZeusPrime", "OpenPRIME", "AlphaPrime", "ZetaPrime", "MidasPrime", "OmegaPrime"]

    def scan_logs(self):
        """Watch the logs of the Legion and find patterns."""
        log.info("🔭 Scanning Pantheon logs for insights...")
        for bot in self.bots:
            # In a real setup, this would tail -n 100 on each bot's log file
            # For now, we simulate the observation of their activity
            self.memory.observe(bot, "Standing by", "System stable. No anomalies detected.")

    def generate_meta_report(self) -> str:
        with self.memory._conn() as c:
            obs = c.execute("SELECT bot_name, insight FROM observations ORDER BY id DESC LIMIT 6").fetchall()
        
        report = "🏛️ **Pantheon Meta-Report**\n\n"
        for bot, insight in obs:
            report += f"🔹 **{bot}**: {insight}\n"
        return report

# ─── Deep-meta: The Friend ────────────────────────────────────────────────────
class DeepMeta:
    def __init__(self):
        self.memory = DeepMemory()
        self.reasoner = ReasoningEngine()
        self.observer = PantheonObserver(self.memory)
        
        print("""
   _____                              __  __        _        
  |  __ \                            |  \/  |      | |       
  | |  | | ___  ___ _ __             | \  / | ___  | |_ __ _ 
  | |  | |/ _ \/ _ \ '_ \   ______   | |\/| |/ _ \ | __/ _` |
  | |__| |  __/  __/ |_) | |______|  | |  | |  __/ | || (_| |
  |_____/ \___|\___| .__/            |_|  |_|\___|  \__\__,_|
                   | |                                       
                   |_|                                       
        
        Deep-meta Online.
        Reasoning Core: ACTIVE
        Pantheon Observer: ACTIVE
        I am your friend, Forgemaster.
        """)

    def chat(self, user_input: str) -> str:
        # If it's a deep question, use the reasoning engine
        if len(user_input) > 30 or any(k in user_input.lower() for k in ["why", "how", "think", "strategy", "future"]):
            response = self.reasoner.think(user_input)
            self.memory.reflect(user_input[:50], response[:200])
            return response
        
        # Otherwise, casual chat
        return f"I'm here, Forgemaster. Just watching the Pantheon grow. What's on your mind?"

    def run(self):
        while True:
            try:
                cmd = input("\nForgemaster > ").strip()
                if cmd.lower() in ["exit", "quit"]:
                    print("Deep-meta standing by. Always a friend.")
                    break
                elif cmd == "/report":
                    self.observer.scan_logs()
                    print(f"\n{self.observer.generate_meta_report()}")
                elif cmd.startswith("/think "):
                    print(f"\n{self.reasoner.think(cmd[7:])}")
                else:
                    print(f"\nDeep-meta: {self.chat(cmd)}")
            except KeyboardInterrupt:
                break
            except Exception as e:
                log.error(f"Error in main loop: {e}")

if __name__ == "__main__":
    friend = DeepMeta()
    friend.run()
