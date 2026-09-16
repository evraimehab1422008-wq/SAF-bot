import os
import re
import sqlite3
from pathlib import Path
from datetime import datetime

from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# =========================================================
# SETTINGS
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

ADMIN_IDS = [
    6448008082,
    8791458947,
]

DB_PATH = os.getenv("DB_PATH", "/data/bot_database.db")
FILES_DIR = Path("/data/files")


if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing from Railway Variables.")


FILES_DIR.mkdir(parents=True, exist_ok=True)
Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


# =========================================================
# STRUCTURE
# =========================================================

STRUCTURE = {
    "🔴 Level 1": {
        "Semester 1": {
            "🦴 Anatomy I": {"Lab": True},
            "🧪 Biochemistry I": {"Lab": False},
            "🔬 Histology": {"Lab": True},
            "🫀 Physiology I": {"Lab": True},
        },
        "Semester 2": {
            "🦴 Anatomy II": {"Lab": True},
            "🧪 Biochemistry II": {"Lab": False},
            "🫀 Physiology II": {"Lab": True},
            "🏃 Kinesiology I": {"Lab": True},
            "⚡ Biophysics": {"Lab": True},
        },
    },

    "🟠 Level 2": {
        "Semester 3": {
            "🧠 Neuroanatomy": {"Lab": True},
            "🦾 Biomechanics II": {"Lab": True},
            "⚡ Electrotherapy I": {"Lab": True},
            "📋 Evaluation I": {"Lab": True},
            "🧠 Neurophysiology": {"Lab": False},
            "🏋️ Therapeutic Ex. I": {"Lab": True},
        },
        "Semester 4": {
            "🦾 Biomechanics III": {"Lab": True},
            "🩺 Community Health": {"Lab": False},
            "📋 Evaluation II": {"Lab": True},
            "🫀 Exercise Physiology": {"Lab": False},
            "🔬 Pathology": {"Lab": False},
            "👐 Manual Therapy": {"Lab": True},
            "⚡ Electrotherapy II": {"Lab": True},
            "🦴 Anatomy IV": {"Lab": True},
            "⚖️ Legal & Ethics": {"Lab": False},
        },
    },

    "🟡 Level 3": {
        "Semester 5": {
            "🦾 Biomechanics IV": {"Lab": True},
            "🌊 Hydrotherapy": {"Lab": True},
            "📊 Research & Statistics": {"Lab": False},
            "💼 Management & Decision": {"Lab": False},
            "🩺 Pathophysiology": {"Lab": False},
            "💊 Pharmacology": {"Lab": False},
            "♿ Rehabilitation": {"Lab": False},
        },
    },

    "🟢 Tracks": {
        "🫀 Batna Track": {
            "🩺 Clin. Med. Cardio": {},
            "🫁 Clin. Med. Chest & Internal": {},
            "👵 Clin. Practice Geriatrics": {},
            "🫀 Clin. Practice Cardio & Pulm.": {},
            "🦯 Geriatric Rehab": {},
            "🫁 P.T. Chest & Internal": {},
            "🫀 P.T. Cardio": {},
            "🥗 Nutrition": {},
            "🧠 Psych. for Handicapped": {},
            "🩻 Radiology": {},
        },

        "🤰 Gyna Track": {
            "🪑 Ergonomics": {},
            "🩺 Clin. Practice Surgery": {},
            "🩹 P.T. Surgery": {},
            "👩‍⚕️ Clin. Practice Womens Health": {},
            "🤰 P.T. Womens Health": {},
            "🩺 Clin. Med. Womens Health": {},
            "📚 Evidence Based Practice": {},
            "🏥 General Surgery & ICU": {},
        },

        "🦴 Ortho Track": {
            "🩺 Clin. Med. Traumatology": {},
            "🦴 Clin. Med. Ortho Surgery": {},
            "📋 Physical Diagnosis": {},
            "🦴 P.T. Orthopedics": {},
            "🦿 Orthotics & Prosthetics": {},
            "🩻 Radiodiagnosis": {},
            "⚽ Sport P.T.": {},
            "🏥 Clin. Practice Ortho": {},
        },

        "👶 Peds Track": {
            "🩺 Clin. Med. Pediatrics": {},
            "👶 Clin. Practice Peds": {},
            "🧸 Motor Development": {},
            "👶 P.T. Pediatrics": {},
            "🏥 P.T. Pediatric Surgery": {},
            "🗣️ Speech Therapy": {},
            "🧩 Occupational Therapy": {},
        },

        "🧠 Neuro Track": {
            "🩺 Clin. Med. Neurology": {},
            "🧠 Clin. Practice Neuro": {},
            "🧠 P.T. Neurology": {},
            "🔪 P.T. Neurosurgery": {},
            "🏥 Neurosurgery": {},
            "🔬 Recent Neuro Rehab": {},
            "⚡ Electrodiagnosis": {},
            "🏃 Motor Learning": {},
        },
    },
}


# =========================================================
# DATABASE
# =========================================================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row

    conn.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path_key TEXT NOT NULL,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(path_key, name)
        )
    """)

    conn.commit()
    return conn


# =========================================================
# HELPERS
# =========================================================

def is_admin(user_id):
    return user_id in ADMIN_IDS


def get_path_key(path):
    if not path:
        return "Home"

    return " / ".join(path)


def sanitize_filename(filename):
    filename = filename.strip()

    filename = re.sub(r'[\\/:*?"<>|]', "_", filename)

    if not filename:
        filename = "file"

    return filename


def get_current_node(path):
    node = STRUCTURE

    for part in path:
        if part in ("Theoretical", "Practical"):
            continue

        if isinstance(node, dict) and part in node:
            node = node[part]
        else:
            return None

    return node


def get_storage_directory(path):
    directory = FILES_DIR

    for part in path:
        safe_part = re.sub(r'[\\/:*?"<>|]', "_", part)
        safe_part = safe_part.strip()

        if not safe_part:
            safe_part = "Unknown"

        directory = directory / safe_part

    directory.mkdir(parents=True, exist_ok=True)

    return directory


def get_files_in_path(path):
    path_key = get_path_key(path)

    conn = get_db()

    rows = conn.execute(
        """
        SELECT id, name, file_path, file_type
        FROM files
        WHERE path_key = ?
        ORDER BY name COLLATE NOCASE
        """,
        (path_key,),
    ).fetchall()

    conn.close()

    return rows


# =========================================================
# MENU
# =========================================================

async def send_menu(update, context):
    path = context.user_data.get("path", [])

    node = get_current_node(path)

    keyboard = []

    # ---------------------------------------------
    # Current location
    # ---------------------------------------------

    if path:
        title = "📍 " + " / ".join(path)
    else:
        title = "🏠 Home"

    # ---------------------------------------------
    # Navigation
    # ---------------------------------------------

    if isinstance(node, dict):

        for key in node.keys():
            keyboard.append([key])

    # ---------------------------------------------
    # Theoretical / Practical
    # ---------------------------------------------

    # Show these only for subjects that actually have Lab
