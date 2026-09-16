import os
import sqlite3
import logging

from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)


# =========================================================
# CONFIGURATION
# =========================================================

BOT_TOKEN = os.getenv("BOT_TOKEN")

# Put Telegram USER IDs of your admins here
ADMIN_IDS = [
    6448008082,
    # Add another admin ID here if needed
]

# Railway:
# Create a Volume mounted at /data
# Then add:
#
# DB_PATH=/data/bot_database.db
#
# For local testing, the default will be:
# bot_database.db

DB_PATH = os.getenv("DB_PATH", "bot_database.db")


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
# BOT STRUCTURE
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
# DATABASE
# =========================================================

def get_connection():
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def init_database():
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path_key TEXT NOT NULL,
            name TEXT NOT NULL,
            file_id TEXT NOT NULL,
            file_type TEXT NOT NULL,
            UNIQUE(path_key, name)
        )
    """)

    connection.commit()
    connection.close()

    logger.info("Database initialized: %s", DB_PATH)


def get_files(path_key):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id, path_key, name, file_id, file_type
        FROM files
        WHERE path_key = ?
        ORDER BY id ASC
    """, (path_key,))

    files = [
        dict(row)
        for row in cursor.fetchall()
    ]

    connection.close()

    return files


def file_exists(path_key, file_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT id
        FROM files
        WHERE path_key = ? AND name = ?
        LIMIT 1
    """, (
        path_key,
        file_name
    ))

    result = cursor.fetchone()

    connection.close()

    return result is not None


def save_file(
    path_key,
    file_name,
    file_id,
    file_type
):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO files (
            path_key,
            name,
            file_id,
            file_type
        )
        VALUES (?, ?, ?, ?)
    """, (
        path_key,
        file_name,
        file_id,
        file_type
    ))

    connection.commit()
    connection.close()


def delete_file(path_key, file_name):
    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        DELETE FROM files
        WHERE path_key = ? AND name = ?
    """, (
        path_key,
        file_name
    ))

    deleted = cursor.rowcount > 0

    connection.commit()
    connection.close()

    return deleted


# =========================================================
# PATH HELPERS
# =========================================================

def get_node(path):
    current = STRUCTURE

    for part in path:

        if (
            isinstance(current, dict)
            and part in current
        ):
            current = current[part]

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

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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

    path = context.user_data.get(
        "path",
        []
    )

    current_node = get_node(path)

    keyboard = []

    # =====================================================
    # STRUCTURE BUTTONS
    # =====================================================

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

        # Normal folder
        else:

            keys = list(current_node.keys())

            for i in range(
                0,
                len(keys),
                2
            ):

                row = [
                    KeyboardButton(keys[i])
                ]

                if i + 1 < len(keys):

                    row.append(
                        KeyboardButton(
                            keys[i + 1]
                        )
                    )

                keyboard.append(row)

    # =====================================================
    # CURRENT LOCATION FILES
    # =====================================================

    path_key = get_path_key(path)

    files = get_files(path_key)

    for file in files:

        if file["file_type"] == "document":

            icon = "📄"

        elif file["file_type"] == "photo":

            icon = "🖼️"

        elif file["file_type"] == "audio":

            icon = "🎙️"

        else:

            icon = "📁"

        keyboard.append([
            KeyboardButton(
                f"{icon} {file['name']}"
            )
        ])

    # =====================================================
    # BACK / HOME
    # =====================================================

    if path:

        keyboard.append([
            KeyboardButton("Back"),
            KeyboardButton("Home")
        ])

    # =====================================================
    # DELETE BUTTON - ADMIN ONLY
    # =====================================================

    if (
        files
        and is_admin(
            update.effective_user.id
        )
    ):

        keyboard.append([
            KeyboardButton(
                "🗑️ Delete File"
            )
        ])

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    # =====================================================
    # MESSAGE
    # =====================================================

    msg_text = (
        f"{text}\n\n"
        f"📍 Current Location:\n"
        f"{path_key}"
    )

    if not files:

        msg_text += (
            "\n\n"
            "📂 No files uploaded "
            "in this location yet."
        )

    if is_admin(
        update.effective_user.id
    ):

        msg_text += (
            "\n\n"
            "⚙️ Admin Mode:\n"
            "Send a PDF, Image, Audio, "
            "or Voice message now.\n"
            "It will be saved in the "
            "CURRENT LOCATION."
        )

    await update.message.reply_text(
        msg_text,
        reply_markup=reply_markup
    )


# =========================================================
# HANDLE TEXT
# =========================================================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if (
        not update.message
        or not update.message.text
    ):
        return

    text = update.message.text.strip()

    if "path" not in context.user_data:

        context.user_data["path"] = []

    path = context.user_data["path"]

    user_id = update.effective_user.id

    # =====================================================
    # HOME
    # =====================================================

    if text in ["Home", "/start"]:

        context.user_data["path"] = []
        context.user_data["deleting_mode"] = False

        await send_menu(
            update,
            context,
            "Home Menu:"
        )

        return

    # =====================================================
    # BACK
    # =====================================================

    if text == "Back":

        if path:

            path.pop()

        context.user_data["path"] = path
        context.user_data["deleting_mode"] = False

        await send_menu(
            update,
            context,
            "Navigating back:"
        )

        return

    # =====================================================
    # DELETE MENU
    # =====================================================

    if text == "🗑️ Delete File":

        if not is_admin(user_id):
            return

        path_key = get_path_key(path)

        files = get_files(path_key)

        if not files:

            await update.message.reply_text(
                "⚠️ No files available to delete."
            )

            return

        context.user_data[
            "deleting_mode"
        ] = True

        delete_keyboard = []

        for i in range(
            0,
            len(files),
            2
        ):

            row = [
                KeyboardButton(
                    f"Delete: {files[i]['name']}"
                )
            ]

            if i + 1 < len(files):

                row.append(
                    KeyboardButton(
                        f"Delete: {files[i + 1]['name']}"
                    )
                )

            delete_keyboard.append(row)

        delete_keyboard.append([
            KeyboardButton("Back"),
            KeyboardButton("Home")
        ])

        await update.message.reply_text(
            "🗑️ Select the file you want to delete:",
            reply_markup=ReplyKeyboardMarkup(
                delete_keyboard,
                resize_keyboard=True
            )
        )

        return

    # =====================================================
    # DELETE SELECTED FILE
    # =====================================================

    if (
        text.startswith("Delete: ")
        and context.user_data.get(
            "deleting_mode"
        )
    ):

        if not is_admin(user_id):
            return

        file_name = text[
            len("Delete: "):
        ]

        path_key = get_path_key(path)

        deleted = delete_file(
            path_key,
            file_name
        )

        context.user_data[
            "deleting_mode"
        ] = False

        if deleted:

            await update.message.reply_text(
                f"🗑️ Deleted successfully:\n"
                f"{file_name}"
            )

        else:

            await update.message.reply_text(
                "⚠️ File was not found."
            )

        await send_menu(
            update,
            context,
            "Updated list:"
        )

        return

    # =====================================================
    # OPEN FILE
    # =====================================================

    path_key = get_path_key(path)

    files = get_files(path_key)

    for file in files:

        if file["name"] in text:

            if file["file_type"] == "document":

                await update.message.reply_document(
                    document=file["file_id"]
                )

            elif file["file_type"] == "photo":

                await update.message.reply_photo(
                    photo=file["file_id"]
                )

            elif file["file_type"] == "audio":

                await update.message.reply_audio(
                    audio=file["file_id"]
                )

            return

    # =====================================================
    # NAVIGATION
    # =====================================================

    current_node = get_node(path)

    matched_key = None

    if isinstance(current_node, dict):

        for key in current_node.keys():

            if (
                key.strip() == text
                and key not in [
                    "type",
                    "lab"
                ]
            ):

                matched_key = key
                break

    if matched_key:

        item = current_node[
            matched_key
        ]

        path.append(matched_key)

        context.user_data[
            "path"
        ] = path

        # -------------------------------------------------
        # SUBJECT
        # -------------------------------------------------

        if (
            isinstance(item, dict)
            and item.get("type") == "subject"
        ):

            keyboard = []

            if item.get("lab"):

                keyboard.append([
                    KeyboardButton(
                        "Theoretical"
                    ),
                    KeyboardButton(
                        "Practical"
                    )
                ])

            else:

                keyboard.append([
                    KeyboardButton(
                        "Theoretical"
                    )
                ])

            keyboard.append([
                KeyboardButton("Back"),
                KeyboardButton("Home")
            ])

            await update.message.reply_text(
                f"Select component for "
                f"{matched_key}:",
                reply_markup=ReplyKeyboardMarkup(
                    keyboard,
                    resize_keyboard=True
                )
            )

            return

        # -------------------------------------------------
        # NORMAL FOLDER
        # -------------------------------------------------

        await send_menu(
            update,
            context,
            f"Selected: {matched_key}"
        )

        return

    # =====================================================
    # THEORETICAL / PRACTICAL
    # =====================================================

    if text in [
        "Theoretical",
        "Practical"
    ]:

        path.append(text)

        context.user_data[
            "path"
        ] = path

        await send_menu(
            update,
            context,
            f"Section: {text}"
        )

        return


# =========================================================
# HANDLE MEDIA UPLOAD
# =========================================================

async def handle_media_upload(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    # =====================================================
    # ONLY ADMINS CAN UPLOAD
    # =====================================================

    if not is_admin(user_id):
        return

    # =====================================================
    # GET CURRENT LOCATION
    # =====================================================

    path = context.user_data.get(
        "path",
        []
    )

    # THIS IS THE IMPORTANT PART:
    # The file is saved EXACTLY where
    # the admin is currently standing.

    path_key = get_path_key(path)

    file_id = None
    file_name = None
    file_type = None

    # =====================================================
    # PDF / DOCUMENT
    # =====================================================

    if update.message.document:

        file_id = update.message.document.file_id

        file_name = (
            update.message.document.file_name
            or "Document"
        )

        # PDF stays a Telegram DOCUMENT
        file_type = "document"

    # =====================================================
    # PHOTO
    # =====================================================

    elif update.message.photo:

        file_id = (
            update.message.photo[-1].file_id
        )

        file_name = (
            update.message.caption
            or (
                f"Photo_"
                f"{len(get_files(path_key)) + 1}"
                f".jpg"
            )
        )

        file_type = "photo"

    # =====================================================
    # AUDIO
    # =====================================================

    elif update.message.audio:

        file_id = update.message.audio.file_id

        file_name = (
            update.message.audio.file_name
            or update.message.caption
            or (
                f"Audio_"
                f"{len(get_files(path_key)) + 1}"
                f".mp3"
            )
        )

        file_type = "audio"

    # =====================================================
    # VOICE
    # =====================================================

    elif update.message.voice:

        file_id = update.message.voice.file_id

        file_name = (
            update.message.caption
            or (
                f"Voice_"
                f"{len(get_files(path_key)) + 1}"
            )
        )

        file_type = "audio"

    else:

        return

    # =====================================================
    # PREVENT DUPLICATE NAME
    # =====================================================

    if file_exists(
        path_key,
        file_name
    ):

        await update.message.reply_text(
            "⚠️ A file with this name "
            "already exists in this location.\n\n"
            f"File: {file_name}\n\n"
            "Please rename the file and "
            "send it again."
        )

        return

    # =====================================================
    # SAVE
    # =====================================================

    try:

        save_file(
            path_key=path_key,
            file_name=file_name,
            file_id=file_id,
            file_type=file_type
        )

    except sqlite3.IntegrityError:

        await update.message.reply_text(
            "⚠️ A file with this name "
            "already exists here."
        )

        return

    except Exception as error:

        logger.exception(
            "Error while saving file: %s",
            error
        )

        await update.message.reply_text(
            "❌ An error occurred while "
            "saving the file."
        )

        return

    # =====================================================
    # SUCCESS
    # =====================================================

    await update.message.reply_text(
        "✅ File saved successfully!\n\n"
        f"📄 {file_name}\n"
        f"📍 Saved in:\n{path_key}"
    )

    # Show current location again
    await send_menu(
        update,
        context,
        "Updated Folder Status:"
    )


# =========================================================
# MAIN
# =========================================================

def main():

    # =====================================================
    # CHECK TOKEN
    # =====================================================

    if not BOT_TOKEN:

        raise RuntimeError(
            "BOT_TOKEN environment variable "
            "is missing."
        )

    # =====================================================
    # DATABASE
    # =====================================================

    init_database()

    # =====================================================
    # APPLICATION
    # =====================================================

    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .build()
    )

    # =====================================================
    # /start
    # =====================================================

    app.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # =====================================================
    # MEDIA
    #
    # PDFs/Documents
    # Photos
    # Audio
    # Voice
    #
    # ALL go to handle_media_upload.
    # =====================================================

    media_filter = (
        filters.Document.ALL
        | filters.PHOTO
        | filters.AUDIO
        | filters.VOICE
    )

    app.add_handler(
        MessageHandler(
            media_filter,
            handle_media_upload
        )
    )

    # =====================================================
    # TEXT
    # =====================================================

    app.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    # =====================================================
    # RUN
    # =====================================================

    logger.info(
        "🤖 Physical Therapy Academic Bot is running..."
    )

    app.run_polling()


# =========================================================
# START PROGRAM
# =========================================================

if __name__ == "__main__":
    main()
