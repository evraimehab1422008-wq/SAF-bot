import os
import logging

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# =========================================================
# SETTINGS
# =========================================================

# Railway Environment Variable
BOT_TOKEN = os.getenv("8791458947:AAFqU8dMWrO3Ov5JjDWMv4OqrIXSZdmaPIY")

# Admin Telegram USER IDs
ADMIN_IDS = [
    6448008082,
    8791458947,
]


# =========================================================
# LOGGING
# =========================================================

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================================================
# ADMIN CHECK
# =========================================================

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS


# =========================================================
# STRUCTURE
# =========================================================

STRUCTURE = {
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

    "🟠 Level 2": {
        "Semester 3": {
            "🧠 Neuroanatomy": {
                "type": "subject",
                "lab": True
            },
            "🦾 Biomechanics II": {
                "type": "subject",
                "lab": True
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

    "🟢 Tracks": {
        "🫀 Batna Track": {
            "🩺 Clin. Med. Cardio": {
                "type": "subject",
                "lab": False
            },
            "🫁 Clin. Med. Chest & Internal": {
                "type": "subject",
                "lab": False
            },
            "👵 Clin. Practice Geriatrics": {
                "type": "subject",
                "lab": True
            },
            "🫀 Clin. Practice Cardio & Pulm.": {
                "type": "subject",
                "lab": True
            },
            "🦯 Geriatric Rehab": {
                "type": "subject",
                "lab": True
            },
            "🫁 P.T. Chest & Internal": {
                "type": "subject",
                "lab": True
            },
            "🫀 P.T. Cardio": {
                "type": "subject",
                "lab": True
            },
            "🥗 Nutrition": {
                "type": "subject",
                "lab": False
            },
            "🧠 Psych. for Handicapped": {
                "type": "subject",
                "lab": False
            },
            "🩻 Radiology": {
                "type": "subject",
                "lab": False
            }
        },

        "🤰 Gyna Track": {
            "🪑 Ergonomics": {
                "type": "subject",
                "lab": True
            },
            "🩺 Clin. Practice Surgery": {
                "type": "subject",
                "lab": True
            },
            "🩹 P.T. Surgery": {
                "type": "subject",
                "lab": True
            },
            "👩‍⚕️ Clin. Practice Womens Health": {
                "type": "subject",
                "lab": True
            },
            "🤰 P.T. Womens Health": {
                "type": "subject",
                "lab": True
            },
            "🩺 Clin. Med. Womens Health": {
                "type": "subject",
                "lab": False
            },
            "📚 Evidence Based Practice": {
                "type": "subject",
                "lab": False
            },
            "🏥 General Surgery & ICU": {
                "type": "subject",
                "lab": False
            }
        },

        "🦴 Ortho Track": {
            "🩺 Clin. Med. Traumatology": {
                "type": "subject",
                "lab": False
            },
            "🦴 Clin. Med. Ortho Surgery": {
                "type": "subject",
                "lab": False
            },
            "📋 Physical Diagnosis": {
                "type": "subject",
                "lab": True
            },
            "🦴 P.T. Orthopedics": {
                "type": "subject",
                "lab": True
            },
            "🦿 Orthotics & Prosthetics": {
                "type": "subject",
                "lab": True
            },
            "🩻 Radiodiagnosis": {
                "type": "subject",
                "lab": False
            },
            "⚽ Sport P.T.": {
                "type": "subject",
                "lab": True
            },
            "🏥 Clin. Practice Ortho": {
                "type": "subject",
                "lab": True
            }
        },

        "👶 Peds Track": {
            "🩺 Clin. Med. Pediatrics": {
                "type": "subject",
                "lab": False
            },
            "👶 Clin. Practice Peds": {
                "type": "subject",
                "lab": True
            },
            "🧸 Motor Development": {
                "type": "subject",
                "lab": True
            },
            "👶 P.T. Pediatrics": {
                "type": "subject",
                "lab": True
            },
            "🏥 P.T. Pediatric Surgery": {
                "type": "subject",
                "lab": True
            },
            "🗣️ Speech Therapy": {
                "type": "subject",
                "lab": False
            },
            "🧩 Occupational Therapy": {
                "type": "subject",
                "lab": False
            }
        },

        "🧠 Neuro Track": {
            "🩺 Clin. Med. Neurology": {
                "type": "subject",
                "lab": False
            },
            "🧠 Clin. Practice Neuro": {
                "type": "subject",
                "lab": True
            },
            "🧠 P.T. Neurology": {
                "type": "subject",
                "lab": True
            },
            "🔪 P.T. Neurosurgery": {
                "type": "subject",
                "lab": True
            },
            "🏥 Neurosurgery": {
                "type": "subject",
                "lab": False
            },
            "🔬 Recent Neuro Rehab": {
                "type": "subject",
                "lab": True
            },
            "⚡ Electrodiagnosis": {
                "type": "subject",
                "lab": True
            },
            "🏃 Motor Learning": {
                "type": "subject",
                "lab": False
            }
        }
    }
}


# =========================================================
# FILE DATABASE
# =========================================================

# IMPORTANT:
# This stores Telegram file_ids in RAM.
#
# It will work while the Railway service is running.
# A later version should use PostgreSQL/SQLite for permanent storage.

file_database = {}


# =========================================================
# HELPER FUNCTIONS
# =========================================================

def get_node(path):
    current = STRUCTURE

    for p in path:

        if isinstance(current, dict) and p in current:
            current = current[p]

        else:
            return None

    return current


def get_path_key(path):
    if path:
        return " -> ".join(path)

    return "Root (Home)"


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["path"] = []
    context.user_data["deleting_mode"] = False

    await send_menu(
        update,
        context,
        "Welcome to Physical Therapy Academic Bot 🩺\n"
        "Select a section:"
    )


# =========================================================
# SEND MENU
# =========================================================

async def send_menu(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    text: str
):

    path = context.user_data.get("path", [])

    current_node = get_node(path)

    keyboard = []

    # -----------------------------------------------------
    # NAVIGATION BUTTONS
    # -----------------------------------------------------

    if isinstance(current_node, dict):

        # Subject
        if current_node.get("type") == "subject":

            if current_node.get("lab"):

                keyboard.append([
                    KeyboardButton("Theoretical"),
                    KeyboardButton("Practical")
                ])

            else:

                keyboard.append([
                    KeyboardButton("Theoretical")
                ])

        # Folder
        else:

            keys = list(current_node.keys())

            for i in range(0, len(keys), 2):

                row = [
                    KeyboardButton(keys[i])
                ]

                if i + 1 < len(keys):

                    row.append(
                        KeyboardButton(keys[i + 1])
                    )

                keyboard.append(row)

    # -----------------------------------------------------
    # CONTROL BUTTONS
    # -----------------------------------------------------

    control_row = []

    if path:

        control_row.append(
            KeyboardButton("Back")
        )

        control_row.append(
            KeyboardButton("Home")
        )

    if control_row:

        keyboard.append(control_row)

    # -----------------------------------------------------
    # ADMIN DELETE BUTTON
    # -----------------------------------------------------

    path_key = get_path_key(path)

    files = file_database.get(path_key, [])

    if files and is_admin(update.effective_user.id):

        keyboard.append([
            KeyboardButton("Delete File")
        ])

    # -----------------------------------------------------
    # REPLY KEYBOARD
    # -----------------------------------------------------

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    # -----------------------------------------------------
    # MESSAGE
    # -----------------------------------------------------

    msg_text = (
        f"{text}\n\n"
        f"📍 Current Location:\n"
        f"`{path_key}`"
    )

    if not files:

        msg_text += (
            "\n\n"
            "📂 No files uploaded in this location yet."
        )

    if is_admin(update.effective_user.id):

        msg_text += (
            "\n\n"
            "⚙️ Admin Mode\n"
            "Send any PDF, Image, or Audio to save it here."
        )

    await update.message.reply_text(
        msg_text,
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )

    # -----------------------------------------------------
    # FILE BUTTONS
    # -----------------------------------------------------
    #
    # IMPORTANT:
    # Files are NOT ReplyKeyboardButtons.
    # They are InlineKeyboardButtons with callback_data.
    #
    # This prevents the PDF name from being treated as text.
    #

    if files:

        file_keyboard = []

        for index, f in enumerate(files):

            if f["type"] == "document":
                icon = "📄"

            elif f["type"] == "photo":
                icon = "🖼️"

            elif f["type"] == "audio":
                icon = "🎙️"

            else:
                icon = "📁"

            file_keyboard.append([
                InlineKeyboardButton(
                    f"{icon} {f['name']}",
                    callback_data=f"FILE_{index}"
                )
            ])

        await update.message.reply_text(
            "📚 Available Files:",
            reply_markup=InlineKeyboardMarkup(
                file_keyboard
            )
        )


# =========================================================
# FILE BUTTON CALLBACK
# =========================================================

async def handle_file_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if not query.data.startswith("FILE_"):
        return

    try:

        index = int(
            query.data.replace("FILE_", "")
        )

    except ValueError:

        await query.message.reply_text(
            "❌ Invalid file."
        )

        return

    path = context.user_data.get("path", [])

    path_key = get_path_key(path)

    files = file_database.get(
        path_key,
        []
    )

    if index < 0 or index >= len(files):

        await query.message.reply_text(
            "❌ File not found."
        )

        return

    file_info = files[index]

    try:

        # -------------------------------------------------
        # DOCUMENT / PDF
        # -------------------------------------------------

        if file_info["type"] == "document":

            await query.message.reply_document(
                document=file_info["file_id"],
                caption=file_info["name"]
            )

        # -------------------------------------------------
        # PHOTO
        # -------------------------------------------------

        elif file_info["type"] == "photo":

            await query.message.reply_photo(
                photo=file_info["file_id"],
                caption=file_info["name"]
            )

        # -------------------------------------------------
        # AUDIO
        # -------------------------------------------------

        elif file_info["type"] == "audio":

            await query.message.reply_audio(
                audio=file_info["file_id"],
                caption=file_info["name"]
            )

    except Exception:

        logger.exception(
            "Failed to send file"
        )

        await query.message.reply_text(
            "❌ I couldn't send this file.\n"
            "The Telegram file may no longer be available."
        )


# =========================================================
# TEXT MESSAGE HANDLER
# =========================================================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    if not update.message.text:
        return

    text = update.message.text.strip()

    if "path" not in context.user_data:

        context.user_data["path"] = []

    path = context.user_data["path"]

    user_id = update.effective_user.id

    # -----------------------------------------------------
    # HOME
    # -----------------------------------------------------

    if text in ["Home", "/start"]:

        context.user_data["path"] = []
        context.user_data["deleting_mode"] = False

        await send_menu(
            update,
            context,
            "Home Menu:"
        )

        return

    # -----------------------------------------------------
    # BACK
    # -----------------------------------------------------

    if text == "Back":

        if path:
