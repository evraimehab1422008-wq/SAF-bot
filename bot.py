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
    if path and len(path) >= 3:

        subject_node = get_current_node(path)

        if isinstance(subject_node, dict):
            if subject_node.get("Lab") is True:
                keyboard.append(["📘 Theoretical", "🧪 Practical"])

    # ---------------------------------------------
    # Files
    # ---------------------------------------------

    files = get_files_in_path(path)

    if files:
        keyboard.append(["📂 Files"])

        for row in files:
            keyboard.append([f"📄 {row['name']}"])

    # ---------------------------------------------
    # Admin delete
    # ---------------------------------------------

    if is_admin(update.effective_user.id) and files:
        keyboard.append(["🗑️ Delete File"])

    # ---------------------------------------------
    # Back
    # ---------------------------------------------

    if path:
        keyboard.append(["⬅️ Back"])

    keyboard.append(["🏠 Home"])

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    text = f"{title}\n\n"

    if files:
        text += f"📁 Files in this location: {len(files)}\n"
    else:
        text += "📁 No files in this location.\n"

    if is_admin(update.effective_user.id):
        text += "\n👑 Admin mode is ON."

    await update.message.reply_text(
        text,
        reply_markup=reply_markup
    )


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["path"] = []
    context.user_data["delete_mode"] = False

    await update.message.reply_text(
        "👋 Welcome to PT Materials Bot"
    )

    await send_menu(update, context)


# =========================================================
# SAVE FILE
# =========================================================

async def handle_media_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # DEBUG
    print("====================================")
    print("DEBUG USER ID:", update.effective_user.id)
    print("DEBUG ADMIN IDS:", ADMIN_IDS)
    print("====================================")

    # ---------------------------------------------
    # Admin check
    # ---------------------------------------------

    if not is_admin(update.effective_user.id):

        await update.message.reply_text(
            "❌ You are not an admin."
        )

        return

    path = context.user_data.get("path", [])

    path_key = get_path_key(path)

    # ---------------------------------------------
    # Detect file
    # ---------------------------------------------

    telegram_file = None
    file_name = None
    file_type = None

    # Document / PDF / TXT / etc.
    if update.message.document:

        telegram_file = await update.message.document.get_file()

        file_name = update.message.document.file_name

        if not file_name:
            file_name = "document"

        file_type = "document"

    # Photo
    elif update.message.photo:

        telegram_file = await update.message.photo[-1].get_file()

        file_name = (
            update.message.caption
            if update.message.caption
            else f"photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        )

        file_type = "photo"

    # Audio
    elif update.message.audio:

        telegram_file = await update.message.audio.get_file()

        file_name = update.message.audio.file_name

        if not file_name:
            file_name = "audio"

        file_type = "audio"

    # Voice
    elif update.message.voice:

        telegram_file = await update.message.voice.get_file()

        file_name = f"voice_{datetime.now().strftime('%Y%m%d_%H%M%S')}.ogg"

        file_type = "voice"

    else:
        return

    # ---------------------------------------------
    # Clean filename
    # ---------------------------------------------

    file_name = sanitize_filename(file_name)

    # ---------------------------------------------
    # Duplicate check
    # ---------------------------------------------

    conn = get_db()

    existing = conn.execute(
        """
        SELECT id
        FROM files
        WHERE path_key = ? AND name = ?
        """,
        (path_key, file_name),
    ).fetchone()

    conn.close()

    if existing:

        await update.message.reply_text(
            f"❌ الملف موجود بالفعل في المكان ده:\n\n"
            f"📄 {file_name}\n\n"
            f"📍 {path_key}"
        )

        return

    # ---------------------------------------------
    # Storage directory
    # ---------------------------------------------

    storage_dir = get_storage_directory(path)

    file_path = storage_dir / file_name

    # ---------------------------------------------
    # Avoid accidental overwrite
    # ---------------------------------------------

    if file_path.exists():

        await update.message.reply_text(
            "❌ الملف موجود بالفعل على الـ Volume."
        )

        return

    # ---------------------------------------------
    # Download
    # ---------------------------------------------

    try:

        await telegram_file.download_to_drive(
            custom_path=str(file_path)
        )

    except Exception as e:

        print("DOWNLOAD ERROR:", repr(e))

        await update.message.reply_text(
            "❌ حصل خطأ أثناء حفظ الملف."
        )

        return

    # ---------------------------------------------
    # Database
    # ---------------------------------------------

    conn = get_db()

    try:

        conn.execute(
            """
            INSERT INTO files
            (
                path_key,
                name,
                file_path,
                file_type,
                created_at
            )
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                path_key,
                file_name,
                str(file_path),
                file_type,
                datetime.now().isoformat(),
            ),
        )

        conn.commit()

    except sqlite3.IntegrityError:

        conn.close()

        if file_path.exists():
            file_path.unlink()

        await update.message.reply_text(
            "❌ الملف موجود بالفعل في نفس المكان."
        )

        return

    conn.close()

    # ---------------------------------------------
    # Success
    # ---------------------------------------------

    await update.message.reply_text(
        f"✅ تم حفظ الملف بنجاح!\n\n"
        f"📄 {file_name}\n"
        f"📍 المكان: {path_key}\n"
        f"💾 Storage: Railway Volume"
    )

    await send_menu(update, context)


# =========================================================
# SEND SAVED FILE
# =========================================================

async def send_saved_file(update, row):

    file_path = Path(row["file_path"])

    if not file_path.exists():

        await update.message.reply_text(
            "❌ الملف مش موجود على الـ Volume."
        )

        return

    try:

        if row["file_type"] == "photo":

            with open(file_path, "rb") as f:
                await update.message.reply_photo(
                    photo=f,
                    caption=row["name"]
                )

        elif row["file_type"] == "audio":

            with open(file_path, "rb") as f:
                await update.message.reply_audio(
                    audio=f,
                    caption=row["name"]
                )

        elif row["file_type"] == "voice":

            with open(file_path, "rb") as f:
                await update.message.reply_voice(
                    voice=f
                )

        else:

            with open(file_path, "rb") as f:
                await update.message.reply_document(
                    document=f,
                    caption=row["name"]
                )

    except Exception as e:

        print("SEND FILE ERROR:", repr(e))

        await update.message.reply_text(
            "❌ حصل خطأ أثناء إرسال الملف."
        )


# =========================================================
# DELETE FILE
# =========================================================

async def delete_file_record(update, context, file_name):

    path = context.user_data.get("path", [])

    path_key = get_path_key(path)

    conn = get_db()

    row = conn.execute(
        """
        SELECT id, file_path
        FROM files
        WHERE path_key = ? AND name = ?
        """,
        (path_key, file_name),
    ).fetchone()

    if not row:

        conn.close()

        await update.message.reply_text(
            "❌ الملف مش موجود."
        )

        return

    file_path = Path(row["file_path"])

    # Delete from DB
    conn.execute(
        """
        DELETE FROM files
        WHERE id = ?
        """,
        (row["id"],)
    )

    conn.commit()
    conn.close()

    # Delete physical file
    if file_path.exists():

        try:
            file_path.unlink()
        except Exception as e:
            print("DELETE PHYSICAL FILE ERROR:", repr(e))

    await update.message.reply_text(
        f"🗑️ تم حذف الملف:\n\n"
        f"📄 {file_name}\n"
        f"📍 {path_key}"
    )


# =========================================================
# MESSAGE HANDLER
# =========================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    if not text:
        return

    path = context.user_data.get("path", [])

    # =====================================================
    # HOME
    # =====================================================

    if text == "🏠 Home":

        context.user_data["path"] = []
        context.user_data["delete_mode"] = False

        await send_menu(update, context)

        return

    # =====================================================
    # BACK
    # =====================================================

    if text == "⬅️ Back":

        if path:
            path.pop()

        context.user_data["path"] = path
        context.user_data["delete_mode"] = False

        await send_menu(update, context)

        return

    # =====================================================
    # DELETE MODE
    # =====================================================

    if text == "🗑️ Delete File":

        if not is_admin(update.effective_user.id):

            await update.message.reply_text(
                "❌ Admin only."
            )

            return

        files = get_files_in_path(path)

        if not files:

            await update.message.reply_text(
                "📁 مفيش ملفات في المكان ده."
            )

            return

        context.user_data["delete_mode"] = True

        keyboard = []

        for row in files:
            keyboard.append([f"🗑️ {row['name']}"])

        keyboard.append(["⬅️ Cancel"])

        await update.message.reply_text(
            "🗑️ اختار الملف اللي عايز تحذفه:",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            )
        )

        return

    # =====================================================
    # CANCEL DELETE
    # =====================================================

    if text == "⬅️ Cancel":

        context.user_data["delete_mode"] = False

        await send_menu(update, context)

        return

    # =====================================================
    # DELETE SELECTED FILE
    # =====================================================

    if context.user_data.get("delete_mode"):

        if not is_admin(update.effective_user.id):

            context.user_data["delete_mode"] = False

            await update.message.reply_text(
                "❌ Admin only."
            )

            return

        if text.startswith("🗑️ "):

            file_name = text[3:].strip()

            context.user_data["delete_mode"] = False

            await delete_file_record(
                update,
                context,
                file_name
            )

            await send_menu(update, context)

            return

    # =====================================================
    # FILE BUTTON
    # =====================================================

    if text.startswith("📄 "):

        file_name = text[3:].strip()

        path_key = get_path_key(path)

        conn = get_db()

        row = conn.execute(
            """
            SELECT id, name, file_path, file_type
            FROM files
            WHERE path_key = ? AND name = ?
            """,
            (path_key, file_name),
        ).fetchone()

        conn.close()

        if not row:

            await update.message.reply_text(
                "❌ الملف مش موجود."
            )

            return

        await send_saved_file(update, row)

        return

    # =====================================================
    # FILES BUTTON
    # =====================================================

    if text == "📂 Files":

        files = get_files_in_path(path)

        if not files:

            await update.message.reply_text(
                "📁 مفيش ملفات هنا."
            )

            return

        message = "📂 الملفات الموجودة:\n\n"

        for index, row in enumerate(files, start=1):

            message += f"{index}. {row['name']}\n"

        await update.message.reply_text(message)

        return

    # =====================================================
    # THEORETICAL / PRACTICAL
    # =====================================================

    if text in ("📘 Theoretical", "🧪 Practical"):

        context.user_data["path"] = path + [text]

        context.user_data["delete_mode"] = False

        await send_menu(update, context)

        return

    # =====================================================
    # NAVIGATION
    # =====================================================

    node = get_current_node(path)

    if isinstance(node, dict):

        if text in node:

            context.user_data["path"] = path + [text]

            context.user_data["delete_mode"] = False

            await send_menu(update, context)

            return

    # =====================================================
    # UNKNOWN
    # =====================================================

    await update.message.reply_text(
        "❓ اختار من الأزرار الموجودة."
    )


# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(update, context):

    print("BOT ERROR:", repr(context.error))


# =========================================================
# MAIN
# =========================================================

def main():

    print("====================================")
    print("PT MATERIALS BOT STARTING")
    print("ADMIN IDS:", ADMIN_IDS)
    print("DB PATH:", DB_PATH)
    print("FILES DIR:", FILES_DIR)
    print("====================================")

    # Initialize DB
    get_db().close()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # /start
    application.add_handler(
        CommandHandler("start", start)
    )

    # Files
    application.add_handler(
        MessageHandler(
            filters.Document.ALL
            | filters.PHOTO
            | filters.AUDIO
            | filters.VOICE,
            handle_media_upload
        )
    )

    # Text
    application.add_handler(
        MessageHandler(
            filters.TEXT & ~filters.COMMAND,
            handle_message
        )
    )

    # Errors
    application.add_error_handler(error_handler)

    print("BOT IS RUNNING...")

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
