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


# =========================
# SETTINGS
# =========================

BOT_TOKEN = os.getenv("BOT_TOKEN")

DB_PATH = os.getenv("DB_PATH", "/data/bot_database.db")
STORAGE_ROOT = Path(os.getenv("STORAGE_ROOT", "/data/storage"))

ADMIN_IDS = {
    6448008082,
    8791458947, 8881717605
}


THEORETICAL = "📚 Theoretical"
PRACTICAL = "🩺 Practical"

BACK = "⬅️ Back"
HOME = "🏠 Home"

DELETE_FILE = "🗑️ Delete File"
CANCEL_DELETE = "❌ Cancel Delete"


# =========================
# STRUCTURE
# =========================

STRUCTURE = {

    # =====================
    # LEVEL 1
    # =====================

    "🔴 Level 1": {

        "Semester 1": {
            "🦴 Anatomy I": {
                "type": "subject",
                "lab": True
            },
            "🧪 Biochemistry I": {
                "type": "subject",
                "lab": False
            },
            "🔬 Histology": {
                "type": "subject",
                "lab": True
            },
            "🫀 Physiology I": {
                "type": "subject",
                "lab": True
            }
        },

        "Semester 2": {
            "🦴 Anatomy II": {
                "type": "subject",
                "lab": True
            },
            "🧪 Biochemistry II": {
                "type": "subject",
                "lab": False
            },
            "🫀 Physiology II": {
                "type": "subject",
                "lab": True
            },
            "🏃 Kinesiology I": {
                "type": "subject",
                "lab": True
            },
            "⚡ Biophysics": {
                "type": "subject",
                "lab": True
            }
        }
    },


    # =====================
    # LEVEL 2
    # =====================

    "🟠 Level 2": {

        "Semester 3": {
            "🧠 Neuroanatomy": {
                "type": "subject",
                "lab": True
            },
            "🦾 Biomechanics II": {
                "type": "subject",
                "lab": False
            },
            "⚡ Electrotherapy I": {
                "type": "subject",
                "lab": True
            },
            "📋 Evaluation I": {
                "type": "subject",
                "lab": True
            },
            "🧠 Neurophysiology": {
                "type": "subject",
                "lab": False
            },
            "🏋️ Therapeutic Ex. I": {
                "type": "subject",
                "lab": True
            }
        },

        "Semester 4": {
            "🦾 Biomechanics III": {
                "type": "subject",
                "lab": True
            },
            "🩺 Community Health": {
                "type": "subject",
                "lab": False
            },
            "📋 Evaluation II": {
                "type": "subject",
                "lab": True
            },
            "🫀 Exercise Physiology": {
                "type": "subject",
                "lab": False
            },
            "🔬 Pathology": {
                "type": "subject",
                "lab": False
            },
            "👐 Manual Therapy": {
                "type": "subject",
                "lab": True
            },
            "⚡ Electrotherapy II": {
                "type": "subject",
                "lab": True
            },
            "🦴 Anatomy IV": {
                "type": "subject",
                "lab": True
            },
            "⚖️ Legal & Ethics": {
                "type": "subject",
                "lab": False
            }
        }
    },


    # =====================
    # LEVEL 3
    # =====================

    "🟡 Level 3": {

        "Semester 5": {
            "🦾 Biomechanics IV": {
                "type": "subject",
                "lab": True
            },
            "🌊 Hydrotherapy": {
                "type": "subject",
                "lab": True
            },
            "📊 Research & Statistics": {
                "type": "subject",
                "lab": False
            },
            "💼 Management & Decision": {
                "type": "subject",
                "lab": False
            },
            "🩺 Pathophysiology": {
                "type": "subject",
                "lab": False
            },
            "💊 Pharmacology": {
                "type": "subject",
                "lab": False
            },
            "♿ Rehabilitation": {
                "type": "subject",
                "lab": False
            }
        }
    },


    # =====================
    # TRACKS
    # =====================

    "🟢 Tracks": {

        # =================
        # 1. Batna
        # =================

        "Batna": {

            'PH pulmonary "CAPU324"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Medicine pulmonary "MED.314PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Geriatric rehabilitation "CAPU326"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'PH cardio "CAPU322"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Medicine cardio "MED.312PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Hospital "CAPU312+CAPU314"': {
                "type": "subject",
                "lecture": False,
                "lab": True
            },

            'Nutrition "BIOC312PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Radiology "RAD.312PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Psychology "PSYCH 312PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            }
        },


        # =================
        # 2. Gyna
        # =================

        "Gyna": {

            'First Aid "FIRS 411E"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Ergonomics "BIOM 411"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Ph Surgery "PT421 / SURG"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'General Surgery "SURG.411"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Ph Gyna "GYPD 421PT"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Med Gyna "MED 411PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Evidence "PT.441"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Hospital Surgery "SURG PT411"': {
                "type": "subject",
                "lecture": False,
                "lab": True
            },

            'Hospital Gyna "GYPD.411"': {
                "type": "subject",
                "lecture": False,
                "lab": True
            }
        },


        # =================
        # 3. Ortho
        # =================

        "Ortho": {

            'PH "MUSK424"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Orthoses & Prosthesis': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Examination "MUSK422"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Sport Physical Therapy': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Hospital "MUSK412"': {
                "type": "subject",
                "lecture": False,
                "lab": True
            },

            'Surgery "SURGPT412"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Medicine "MED412PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Radiology "RAD.412PT"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            }
        },


        # =================
        # 4. Neuro
        # =================

        "Neuro": {

            'Topic "NEUR526"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Motor "PT541"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'medicine "MED512PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'spinal "NEUR524"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Neurosurgery "SURG512PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'PH "NEUR.522"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'EMG "NEUR.525"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Hospital "NEUR512" + Spinal sec': {
                "type": "subject",
                "lecture": False,
                "lab": True
            }
        },


        # =================
        # 5. Peds
        # =================

        "Peds": {

            'Hospital "GYPD 511"': {
                "type": "subject",
                "lecture": False,
                "lab": True
            },

            'Ph "GYPD 525"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Surgery "GYPD 527"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Motor development "GYPD 521"': {
                "type": "subject",
                "lecture": True,
                "lab": True
            },

            'Speech Therapy "GYPD 529"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Occupational Therapy "OT.511"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            },

            'Medicine "MED.511PT"': {
                "type": "subject",
                "lecture": True,
                "lab": False
            }
        }
    }
}


# =========================
# DATABASE
# =========================

def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    conn = get_db()

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
    conn.close()


# =========================
# HELPERS
# =========================

def is_admin(user_id):
    return user_id in ADMIN_IDS


def get_path_key(path):
    return " / ".join(path)


def sanitize_filename(filename):
    filename = filename.strip()
    filename = re.sub(r'[<>:"/\\|?*]', "_", filename)
    filename = filename.rstrip(". ")
    return filename or "file"


def get_current_node(path):
    node = STRUCTURE

    for part in path:

        # Theoretical / Practical are navigation sections,
        # not keys inside STRUCTURE.
        if part in (THEORETICAL, PRACTICAL):
            continue

        if not isinstance(node, dict):
            return None

        if part not in node:
            return None

        node = node[part]

    return node


def get_storage_directory(path):
    directory = STORAGE_ROOT

    for part in path:
        safe_part = sanitize_filename(part)
        directory = directory / safe_part

    directory.mkdir(parents=True, exist_ok=True)

    return directory


def get_files_in_path(path):
    path_key = get_path_key(path)

    conn = get_db()

    rows = conn.execute(
        """
        SELECT *
        FROM files
        WHERE path_key = ?
        ORDER BY id ASC
        """,
        (path_key,)
    ).fetchall()

    conn.close()

    return rows


def get_file_by_name(path, filename):
    path_key = get_path_key(path)

    conn = get_db()

    row = conn.execute(
        """
        SELECT *
        FROM files
        WHERE path_key = ? AND name = ?
        """,
        (path_key, filename)
    ).fetchone()

    conn.close()

    return row


# =========================
# MENU
# =========================

async def send_menu(update, context, path=None, delete_mode=False):

    if path is None:
        path = context.user_data.get("path", [])

    context.user_data["path"] = path
    context.user_data["delete_mode"] = delete_mode

    node = get_current_node(path)

    if node is None:
        await update.message.reply_text("❌ Invalid location.")
        return

    buttons = []

    # =====================
    # DELETE MODE
    # =====================

    if delete_mode:

        files = get_files_in_path(path)

        if not files:
            context.user_data["delete_mode"] = False
            await send_menu(update, context, path, False)
            return

        for file in files:
            buttons.append([file["name"]])

        buttons.append([CANCEL_DELETE])

        await update.message.reply_text(
            "🗑️ Choose the file you want to delete:",
            reply_markup=ReplyKeyboardMarkup(
                buttons,
                resize_keyboard=True
            )
        )

        return


    # =====================
    # NORMAL NAVIGATION
    # =====================

    # Subject node
    if isinstance(node, dict) and node.get("type") == "subject":

        # For old subjects:
        # if lecture is not explicitly defined,
        # treat it as True.
        lecture = node.get("lecture", True)
        lab = node.get("lab", False)

        subject_buttons = []

        if lecture:
            subject_buttons.append(THEORETICAL)

        if lab:
            subject_buttons.append(PRACTICAL)

        if len(subject_buttons) == 2:
            buttons.append([
                subject_buttons[0],
                subject_buttons[1]
            ])

        elif len(subject_buttons) == 1:
            buttons.append([subject_buttons[0]])

    else:

        # Normal navigation
        if isinstance(node, dict):

            navigation_buttons = []

            for name, value in node.items():

                if isinstance(value, dict) and value.get("type") == "subject":
                    navigation_buttons.append(name)

                elif isinstance(value, dict):
                    navigation_buttons.append(name)

            # Two columns
            for i in range(0, len(navigation_buttons), 2):

                row = navigation_buttons[i:i + 2]

                buttons.append(row)

    # =====================
    # FILES
    # =====================

    files = get_files_in_path(path)

    for file in files:
        buttons.append([file["name"]])

    # =====================
    # ADMIN DELETE BUTTON
    # =====================

    if is_admin(update.effective_user.id) and files:
        buttons.append([DELETE_FILE])

    # =====================
    # BACK / HOME
    # =====================

    if path:
        buttons.append([BACK, HOME])

    # =====================
    # HOME PAGE
    # =====================

    if not path:
        # No Home button on initial Home page.
        pass

    await update.message.reply_text(
        "📚 PT Materials\n\n"
        + ("📍 " + get_path_key(path) if path else "🏠 Home"),
        reply_markup=ReplyKeyboardMarkup(
            buttons,
            resize_keyboard=True
        )
    )


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["path"] = []
    context.user_data["delete_mode"] = False

    await update.message.reply_text(
        "👋 Welcome to PT Materials Bot!"
    )

    await send_menu(
        update,
        context,
        []
    )


# =========================
# SEND SAVED FILE
# =========================

async def send_saved_file(update, file):

    file_path = file["file_path"]
    file_type = file["file_type"]

    if not os.path.exists(file_path):
        await update.message.reply_text(
            "❌ This file is no longer available."
        )
        return

    with open(file_path, "rb") as f:

        if file_type == "document":
            await update.message.reply_document(
                document=f,
                filename=file["name"]
            )

        elif file_type == "photo":
            await update.message.reply_photo(
                photo=f
            )

        elif file_type == "audio":
            await update.message.reply_audio(
                audio=f,
                filename=file["name"]
            )

        elif file_type == "voice":
            await update.message.reply_voice(
                voice=f
            )


# =========================
# MEDIA UPLOAD
# =========================

async def handle_media_upload(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ Admins only."
        )
        return

    path = context.user_data.get("path", [])

    # ---------------------
    # Document
    # ---------------------

    if update.message.document:

        media = update.message.document

        filename = media.file_name or "document"

        file_type = "document"

    # ---------------------
    # Photo
    # ---------------------

    elif update.message.photo:

        media = update.message.photo[-1]

        filename = f"photo_{media.file_unique_id}.jpg"

        file_type = "photo"

    # ---------------------
    # Audio
    # ---------------------

    elif update.message.audio:

        media = update.message.audio

        filename = media.file_name or "audio"

        file_type = "audio"

    # ---------------------
    # Voice
    # ---------------------

    elif update.message.voice:

        media = update.message.voice

        filename = f"voice_{media.file_unique_id}.ogg"

        file_type = "voice"

    else:
        return

    filename = sanitize_filename(filename)

    # ---------------------
    # Duplicate check
    # ---------------------

    existing = get_file_by_name(path, filename)

    if existing:
        await update.message.reply_text(
            f'❌ File "{filename}" already exists in th
