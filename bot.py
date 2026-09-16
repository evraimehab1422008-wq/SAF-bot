import os
import re
import sqlite3
from pathlib import Path
from datetime import datetime

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    ReplyKeyboardRemove,
)
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

# YOUR TWO ADMINS
ADMIN_IDS = [
    6448008082,
    8791458947,
]

DB_PATH = os.getenv("DB_PATH", "/data/bot_database.db")

# All uploaded files will be stored here.
FILES_DIR = Path("/data/files")


# =========================================================
# CHECK SETTINGS
# =========================================================

if not BOT_TOKEN:
    raise RuntimeError("BOT_TOKEN is missing from Railway Variables.")

FILES_DIR.mkdir(parents=True, exist_ok=True)

Path(DB_PATH).parent.mkdir(parents=True, exist_ok=True)


# =========================================================
# BOT STRUCTURE
# =========================================================

STRUCTURE = {
    "🔴 Level 1": {
        "Semester 1": {
            "🦴 Anatomy I": {"lab": True},
            "🧪 Biochemistry I": {"lab": False},
            "🔬 Histology": {"lab": True},
            "🫀 Physiology I": {"lab": True},
        },
        "Semester 2": {
            "🦴 Anatomy II": {"lab": True},
            "🧪 Biochemistry II": {"lab": False},
            "🫀 Physiology II": {"lab": True},
            "🏃 Kinesiology I": {"lab": True},
            "⚡ Biophysics": {"lab": True},
        },
    },

    "🟠 Level 2": {
        "Semester 3": {
            "🧠 Neuroanatomy": {"lab": True},
            "🦾 Biomechanics II": {"lab": True},
            "⚡ Electrotherapy I": {"lab": True},
            "📋 Evaluation I": {"lab": True},
            "🧠 Neurophysiology": {"lab": False},
            "🏋️ Therapeutic Ex. I": {"lab": True},
        },
        "Semester 4": {
            "🦾 Biomechanics III": {"lab": True},
            "🩺 Community Health": {"lab": False},
            "📋 Evaluation II": {"lab": True},
            "🫀 Exercise Physiology": {"lab": False},
            "🔬 Pathology": {"lab": False},
            "👐 Manual Therapy": {"lab": True},
            "⚡ Electrotherapy II": {"lab": True},
            "🦴 Anatomy IV": {"lab": True},
            "⚖️ Legal & Ethics": {"lab": False},
        },
    },

    "🟡 Level 3": {
        "Semester 5": {
            "🦾 Biomechanics IV": {"lab": True},
            "🌊 Hydrotherapy": {"lab": True},
            "📊 Research & Statistics": {"lab": False},
            "💼 Management & Decision": {"lab": False},
            "🩺 Pathophysiology": {"lab": False},
            "💊 Pharmacology": {"lab": False},
            "♿ Rehabilitation": {"lab": False},
        },
    },

    "🟢 Tracks": {
        "🫀 Batna Track": {
            "🩺 Clin. Med. Cardio": {"lab": False},
            "🫁 Clin. Med. Chest & Internal": {"lab": False},
            "👵 Clin. Practice Geriatrics": {"lab": False},
            "🫀 Clin. Practice Cardio & Pulm.": {"lab": False},
            "🦯 Geriatric Rehab": {"lab": False},
            "🫁 P.T. Chest & Internal": {"lab": False},
            "🫀 P.T. Cardio": {"lab": False},
            "🥗 Nutrition": {"lab": False},
            "🧠 Psych. for Handicapped": {"lab": False},
            "🩻 Radiology": {"lab": False},
        },

        "🤰 Gyna Track": {
            "🪑 Ergonomics": {"lab": False},
            "🩺 Clin. Practice Surgery": {"lab": False},
            "🩹 P.T. Surgery": {"lab": False},
            "👩‍⚕️ Clin. Practice Womens Health": {"lab": False},
            "🤰 P.T. Womens Health": {"lab": False},
            "🩺 Clin. Med. Womens Health": {"lab": False},
            "📚 Evidence Based Practice": {"lab": False},
            "🏥 General Surgery & ICU": {"lab": False},
        },

        "🦴 Ortho Track": {
            "🩺 Clin. Med. Traumatology": {"lab": False},
            "🦴 Clin. Med. Ortho Surgery": {"lab": False},
            "📋 Physical Diagnosis": {"lab": False},
            "🦴 P.T. Orthopedics": {"lab": False},
            "🦿 Orthotics & Prosthetics": {"lab": False},
            "🩻 Radiodiagnosis": {"lab": False},
            "⚽ Sport P.T.": {"lab": False},
            "🏥 Clin. Practice Ortho": {"lab": False},
        },

        "👶 Peds Track": {
            "🩺 Clin. Med. Pediatrics": {"lab": False},
            "👶 Clin. Practice Peds": {"lab": False},
            "🧸 Motor Development": {"lab": False},
            "👶 P.T. Pediatrics": {"lab": False},
            "🏥 P.T. Pediatric Surgery": {"lab": False},
            "🗣️ Speech Therapy": {"lab": False},
            "🧩 Occupational Therapy": {"lab": False},
        },

        "🧠 Neuro Track": {
            "🩺 Clin. Med. Neurology": {"lab": False},
            "🧠 Clin. Practice Neuro": {"lab": False},
            "🧠 P.T. Neurology": {"lab": False},
            "🔪 P.T. Neurosurgery": {"lab": False},
            "🏥 Neurosurgery": {"lab": False},
            "🔬 Recent Neuro Rehab": {"lab": False},
            "⚡ Electrodiagnosis": {"lab": False},
            "🏃 Motor Learning": {"lab": False},
        },
    },
}


# =========================================================
# DATABASE
# =========================================================

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_database():
    conn = get_connection()

    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            path_key TEXT NOT NULL,
            name TEXT NOT NULL,
            file_path TEXT NOT NULL,
            file_type TEXT NOT NULL,
            created_at TEXT NOT NULL,
            UNIQUE(path_key, name)
        )
        """
    )

    conn.commit()
    conn.close()


def get_files(path_key):
    conn = get_connection()

    rows = conn.execute(
        """
        SELECT *
        FROM files
        WHERE path_key = ?
        ORDER BY id ASC
        """,
        (path_key,),
    ).fetchall()

    conn.close()
    return rows


def get_file_by_id(file_id):
    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM files
        WHERE id = ?
        """,
        (file_id,),
    ).fetchone()

    conn.close()
    return row


def file_exists(path_key, name):
    conn = get_connection()

    row = conn.execute(
        """
        SELECT id
        FROM files
        WHERE path_key = ? AND name = ?
        """,
        (path_key, name),
    ).fetchone()

    conn.close()

    return row is not None


def save_file_record(path_key, name, file_path, file_type):
    conn = get_connection()

    cursor = conn.execute(
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
            name,
            str(file_path),
            file_type,
            datetime.now().isoformat(),
        ),
    )

    file_id = cursor.lastrowid

    conn.commit()
    conn.close()

    return file_id


def delete_file_record(file_id):
    conn = get_connection()

    row = conn.execute(
        """
        SELECT *
        FROM files
        WHERE id = ?
        """,
        (file_id,),
    ).fetchone()

    if not row:
        conn.close()
        return False

    conn.execute(
        """
        DELETE FROM files
        WHERE id = ?
        """,
        (file_id,),
    )

    conn.commit()
    conn.close()

    try:
        Path(row["file_path"]).unlink(missing_ok=True)
    except Exception:
        pass

    return True


# =========================================================
# HELPERS
# =========================================================

def is_admin(user_id):
    return user_id in ADMIN_IDS


def sanitize_filename(name):
    if not name:
        name = "file"

    name = name.replace("/", "_")
    name = name.replace("\\", "_")
    name = re.sub(r'[<>:"|?*\x00-\x1F]', "_", name)

    name = name.strip()

    if not name:
        name = "file"

    return name


def get_path_key(path):
    if not path:
        return "Home"

    return " / ".join(path)


def get_current_node(path):
    node = STRUCTURE

    for item in path:
        if isinstance(node, dict) and item in node:
            node = node[item]
        else:
            return None

    return node


def is_subject(path):
    node = get_current_node(path)

    return isinstance(node, dict) and "lab" in node


def safe_folder_name(name):
    name = sanitize_filename(name)
    return name[:100]


def get_storage_directory(path):
    directory = FILES_DIR

    for part in path:
        directory = directory / safe_folder_name(part)

    directory.mkdir(parents=True, exist_ok=True)

    return directory


# =========================================================
# MENU
# =========================================================

async def send_menu(update, context):
    path = context.user_data.get("path", [])
    deleting = context.user_data.get("deleting", False)

    path_key = get_path_key(path)
    node = get_current_node(path)

    keyboard = []

    # -------------------------
    # DELETE MODE
    # -------------------------

    if deleting:
        files = get_files(path_key)

        if not files:
            context.user_data["deleting"] = False

            await update.message.reply_text(
                "❌ مفيش ملفات في المكان ده."
            )

            return await send_menu(update, context)

        keyboard.append(["🔙 Cancel Delete"])

        for file in files:
            keyboard.append([f"🗑️ {file['name']}"])

        keyboard.append(["🏠 Home"])

        await update.message.reply_text(
            f"🗑️ اختار الملف اللي عايز تحذفه:\n\n"
            f"📍 المكان الحالي:\n{path_key}",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            ),
        )

        return

    # -------------------------
    # NORMAL MODE
    # -------------------------

    if isinstance(node, dict):

        # If this is a subject
        if "lab" in node:
            keyboard.append(["📚 Theoretical"])

            if node.get("lab"):
                keyboard.append(["🔬 Practical"])

        else:
            for key in node.keys():
                keyboard.append([key])

    # -------------------------
    # FILES
    # -------------------------

    files = get_files(path_key)

    if files:
        keyboard.append(["📂 Files"])

        for file in files:
            keyboard.append([f"📄 {file['name']}"])

    # -------------------------
    # ADMIN DELETE
    # -------------------------

    if is_admin(update.effective_user.id) and files:
        keyboard.append(["🗑️ Delete File"])

    # -------------------------
    # NAVIGATION
    # -------------------------

    if path:
        keyboard.append(["🔙 Back"])

    keyboard.append(["🏠 Home"])

    location_text = get_path_key(path)

    text = (
        f"📍 Current Location:\n"
        f"{location_text}\n\n"
        f"اختار من القائمة:"
    )

    await update.message.reply_text(
        text,
        reply_markup=ReplyKeyboardMarkup(
            keyboard,
            resize_keyboard=True
        ),
    )


# =========================================================
# START
# =========================================================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["path"] = []
    context.user_data["deleting"] = False

    await send_menu(update, context)


# =========================================================
# SEND SAVED FILE
# =========================================================

async def send_saved_file(update, file):
    file_path = Path(file["file_path"])

    if not file_path.exists():
        await update.message.reply_text(
            "❌ الملف ده مش موجود فعليًا على التخزين."
        )
        return

    file_type = file["file_type"]

    try:
        if file_type == "document":
            with open(file_path, "rb") as f:
                await update.message.reply_document(
                    document=f,
                    caption=file["name"]
                )

        elif file_type == "photo":
            with open(file_path, "rb") as f:
                await update.message.reply_photo(
                    photo=f,
                    caption=file["name"]
                )

        elif file_type == "audio":
            with open(file_path, "rb") as f:
                await update.message.reply_audio(
                    audio=f,
                    caption=file["name"]
                )

        elif file_type == "voice":
            with open(file_path, "rb") as f:
                await update.message.reply_voice(
                    voice=f
                )

        else:
            with open(file_path, "rb") as f:
                await update.message.reply_document(
                    document=f,
                    caption=file["name"]
                )

    except Exception as e:
        await update.message.reply_text(
            f"❌ حصل خطأ أثناء إرسال الملف:\n{e}"
        )


# =========================================================
# DOWNLOAD / SAVE MEDIA
# =========================================================

async def handle_media_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not is_admin(user_id):
        await update.message.reply_text(
            "❌ إضافة الملفات متاحة للأدمنز فقط."
        )
        return

    path = context.user_data.get("path", [])
    path_key = get_path_key(path)

    # -------------------------
    # DOCUMENT
    # -------------------------

    if update.message.document:
        telegram_file = update.message.document

        filename = telegram_file.file_name or "document"
        filename = sanitize_filename(filename)

        file_type = "document"

        telegram_obj = await context.bot.get_file(
            telegram_file.file_id
        )

    # -------------------------
    # PHOTO
    # -------------------------

    elif update.message.photo:
        telegram_file = update.message.photo[-1]

        filename = (
            f"photo_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.jpg"
        )

        file_type = "photo"

        telegram_obj = await context.bot.get_file(
            telegram_file.file_id
        )

    # -------------------------
    # AUDIO
    # -------------------------

    elif update.message.audio:
        telegram_file = update.message.audio

        filename = (
            telegram_file.file_name
            or f"audio_{datetime.now().strftime('%Y%m%d_%H%M%S')}.mp3"
        )

        filename = sanitize_filename(filename)

        file_type = "audio"

        telegram_obj = await context.bot.get_file(
            telegram_file.file_id
        )

    # -------------------------
    # VOICE
    # -------------------------

    elif update.message.voice:
        telegram_file = update.message.voice

        filename = (
            f"voice_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.ogg"
        )

        file_type = "voice"

        telegram_obj = await context.bot.get_file(
            telegram_file.file_id
        )

    else:
        return

    # -------------------------
    # DUPLICATE CHECK
    # -------------------------

    if file_exists(path_key, filename):
        await update.message.reply_text(
            f"❌ فيه ملف بنفس الاسم موجود بالفعل هنا:\n\n"
            f"📄 {filename}\n\n"
            f"غير اسم الملف وحاول تاني."
        )
        return

    # -------------------------
    # STORAGE DIRECTORY
    # -------------------------

    directory = get_storage_directory(path)

    file_path = directory / filename

    # -------------------------
    # DOWNLOAD TO RAILWAY VOLUME
    # -------------------------

    try:
        await telegram_obj.download_to_drive(
            custom_path=str(file_path)
        )

    except Exception as e:
        await update.message.reply_text(
            f"❌ حصل خطأ أثناء حفظ الملف:\n{e}"
        )
        return

    # -------------------------
    # DATABASE
    # -------------------------

    try:
        save_file_record(
            path_key=path_key,
            name=filename,
            file_path=file_path,
            file_type=file_type,
        )

    except Exception as e:

        try:
            file_path.unlink(missing_ok=True)
        except Exception:
            pass

        await update.message.reply_text(
            f"❌ حصل خطأ في قاعدة البيانات:\n{e}"
        )

        return

    await update.message.reply_text(
        f"✅ تم حفظ الملف بنجاح!\n\n"
        f"📄 {filename}\n\n"
        f"📍 المكان:\n{path_key}"
    )

    await send_menu(update, context)


# =========================================================
# TEXT HANDLER
# =========================================================

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    text = update.message.text

    user_id = update.effective_user.id

    path = context.user_data.get("path", [])
    path_key = get_path_key(path)

    # =====================================================
    # DELETE MODE
    # =====================================================

    if context.user_data.get("deleting"):

        if not is_admin(user_id):
            context.user_data["deleting"] = False
            await update.message.reply_text(
                "❌ غير مسموح."
            )
            return

        if text == "🔙 Cancel Delete":
            context.user_data["deleting"] = False
            await send_menu(update, context)
            return

        if text == "🏠 Home":
            context.user_data["path"] = []
            context.user_data["deleting"] = False
            await send_menu(update, context)
            return

        if text.startswith("🗑️ "):

            filename = text[3:].strip()

            files = get_files(path_key)

            selected = None

            for file in files:
                if file["name"] == filename:
                    selected = file
                    break

            if not selected:
                await update.message.reply_text(
                    "❌ الملف ده مش موجود في المكان الحالي."
                )
                return

            delete_file_record(selected["id"])

            context.user_data["deleting"] = False

            await update.message.reply_text(
                f"✅ تم حذف الملف:\n\n"
                f"📄 {filename}"
            )

            await send_menu(update, context)

            return

    # =====================================================
    # HOME
    # =====================================================

    if text == "🏠 Home":

        context.user_data["path"] = []
        context.user_data["deleting"] = False

        await send_menu(update, context)

        return

    # =====================================================
    # BACK
    # =====================================================

    if text == "🔙 Back":

        if path:
            path.pop()

        context.user_data["path"] = path
        context.user_data["deleting"] = False

        await send_menu(update, context)

        return

    # =====================================================
    # DELETE FILE
    # =====================================================

    if text == "🗑️ Delete File":

        if not is_admin(user_id):
            await update.message.reply_text(
                "❌ الأمر ده للأدمنز فقط."
            )
            return

        files = get_files(path_key)

        if not files:
            await update.message.reply_text(
                "❌ مفيش ملفات في المكان الحالي."
            )
            return

        context.user_data["deleting"] = True

        await send_menu(update, context)

        return

    # =====================================================
    # FILE OPENING
    # =====================================================

    if text.startswith("📄 "):

        filename = text[3:].strip()

        files = get_files(path_key)

        selected = None

        for file in files:
            if file["name"] == filename:
                selected = file
                break

        if selected:
            await send_saved_file(update, selected)

        return

    # =====================================================
    # FILES BUTTON
    # =====================================================

    if text == "📂 Files":

        files = get_files(path_key)

        if not files:
            await update.message.reply_text(
                "❌ مفيش ملفات هنا."
            )
            return

        keyboard = []

        for file in files:
            keyboard.append([f"📄 {file['name']}"])

        if is_admin(user_id):
            keyboard.append(["🗑️ Delete File"])

        keyboard.append(["🔙 Back"])
        keyboard.append(["🏠 Home"])

        await update.message.reply_text(
            f"📂 Files in:\n{path_key}",
            reply_markup=ReplyKeyboardMarkup(
                keyboard,
                resize_keyboard=True
            ),
        )

        return

    # =====================================================
    # THEORETICAL / PRACTICAL
    # =====================================================

    if text == "📚 Theoretical":

        context.user_data["path"] = path + ["Theoretical"]

        await send_menu(update, context)

        return

    if text == "🔬 Practical":

        context.user_data["path"] = path + ["Practical"]

        await send_menu(update, context)

        return

    # =====================================================
    # NAVIGATION
    # =====================================================

    node = get_current_node(path)

    if isinstance(node, dict):

        if text in node:

            context.user_data["path"] = path + [text]
            context.user_data["deleting"] = False

            await send_menu(update, context)

            return

    # =====================================================
    # UNKNOWN TEXT
    # =====================================================

    await update.message.reply_text(
        "اختار من الأزرار الموجودة تحت 👇"
    )


# =========================================================
# ERROR HANDLER
# =========================================================

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE):

    print("ERROR:", context.error)


# =========================================================
# MAIN
# =========================================================

def main():

    init_database()

    application = (
        Application.builder()
        .token(BOT_TOKEN)
        .build()
    )

    # /start
    application.add_handler(
        CommandHandler("start", start)
    )

    # Documents / Photos / Audio / Voice
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

    application.add_error_handler(error_handler)

    print("Bot is starting...")
    print("Admins:", ADMIN_IDS)
    print("Database:", DB_PATH)
    print("Files directory:", FILES_DIR)

    application.run_polling(
        drop_pending_updates=True
    )


if __name__ == "__main__":
    main()
