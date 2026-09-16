import os
import logging
import uuid

from telegram import (
    Update,
    ReplyKeyboardMarkup,
    KeyboardButton,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ContextTypes,
    filters,
)

# =========================
# BOT SETTINGS
# =========================

BOT_TOKEN = os.getenv("8791458947:AAFqU8dMWrO3Ov5JjDWMv4OqrIXSZdmaPIY")

# نفس الـ Admins بتوعك
ADMIN_IDS = [
    6448008082,
    8791458947,
]

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)

logger = logging.getLogger(__name__)


# =========================
# STRUCTURE
# =========================

STRUCTURE = {
    "🔴 Level 1": {
        "Semester 1": [
            "🦴 Anatomy I",
            "🧪 Biochemistry I",
            "🔬 Histology",
            "🫀 Physiology I",
        ],
        "Semester 2": [
            "🦴 Anatomy II",
            "🧪 Biochemistry II",
            "🫀 Physiology II",
            "🏃 Kinesiology I",
            "⚡ Biophysics",
        ],
    },

    "🟠 Level 2": {
        "Semester 3": [
            "🧠 Neuroanatomy",
            "🦾 Biomechanics II",
            "⚡ Electrotherapy I",
            "📋 Evaluation I",
            "🧠 Neurophysiology",
            "🏋️ Therapeutic Ex. I",
        ],

        "Semester 4": [
            "🦾 Biomechanics III",
            "🩺 Community Health",
            "📋 Evaluation II",
            "🫀 Exercise Physiology",
            "🔬 Pathology",
            "👐 Manual Therapy",
            "⚡ Electrotherapy II",
            "🦴 Anatomy IV",
            "⚖️ Legal & Ethics",
        ],
    },

    "🟡 Level 3": {
        "Semester 5": [
            "🦾 Biomechanics IV",
            "🌊 Hydrotherapy",
            "📊 Research & Statistics",
            "💼 Management & Decision",
            "🩺 Pathophysiology",
            "💊 Pharmacology",
            "♿ Rehabilitation",
        ],
    },

    "🟢 Tracks": {
        "🫀 Batna Track": [
            "🩺 Clin. Med. Cardio",
            "🫁 Clin. Med. Chest & Internal",
            "👵 Clin. Practice Geriatrics",
            "🫀 Clin. Practice Cardio & Pulm.",
            "🦯 Geriatric Rehab",
            "🫁 P.T. Chest & Internal",
            "🫀 P.T. Cardio",
            "🥗 Nutrition",
            "🧠 Psych. for Handicapped",
            "🩻 Radiology",
        ],

        "🤰 Gyna Track": [
            "🪑 Ergonomics",
            "🩺 Clin. Practice Surgery",
            "🩹 P.T. Surgery",
            "👩‍⚕️ Clin. Practice Womens Health",
            "🤰 P.T. Womens Health",
            "🩺 Clin. Med. Womens Health",
            "📚 Evidence Based Practice",
            "🏥 General Surgery & ICU",
        ],

        "🦴 Ortho Track": [
            "🩺 Clin. Med. Traumatology",
            "🦴 Clin. Med. Ortho Surgery",
            "📋 Physical Diagnosis",
            "🦴 P.T. Orthopedics",
            "🦿 Orthotics & Prosthetics",
            "🩻 Radiodiagnosis",
            "⚽ Sport P.T.",
            "🏥 Clin. Practice Ortho",
        ],

        "👶 Peds Track": [
            "🩺 Clin. Med. Pediatrics",
            "👶 Clin. Practice Peds",
            "🧸 Motor Development",
            "👶 P.T. Pediatrics",
            "🏥 P.T. Pediatric Surgery",
            "🗣️ Speech Therapy",
            "🧩 Occupational Therapy",
        ],

        "🧠 Neuro Track": [
            "🩺 Clin. Med. Neurology",
            "🧠 Clin. Practice Neuro",
            "🧠 P.T. Neurology",
            "🔪 P.T. Neurosurgery",
            "🏥 Neurosurgery",
            "🔬 Recent Neuro Rehab",
            "⚡ Electrodiagnosis",
            "🏃 Motor Learning",
        ],
    },
}


# =========================
# FILE DATABASE
# =========================

# الملفات بتفضل في الـRAM طول ما البوت شغال
file_database = {}


# =========================
# HELPERS
# =========================

def is_admin(user_id):
    return user_id in ADMIN_IDS


def get_node(path):
    node = STRUCTURE

    for part in path:
        if isinstance(node, dict):
            node = node.get(part)

        elif isinstance(node, list):
            if part in node:
                return part
            return None

        else:
            return None

    return node


def get_current_path_key(path):
    if not path:
        return "Root (Home)"

    return " -> ".join(path)


def get_file_icon(file_type):
    if file_type == "document":
        return "📄"

    if file_type == "photo":
        return "🖼️"

    if file_type == "audio":
        return "🎵"

    if file_type == "voice":
        return "🎤"

    return "📎"


# =========================
# START
# =========================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):

    context.user_data["path"] = []
    context.user_data["deleting_mode"] = False

    await send_menu(update, context)


# =========================
# SEND MENU
# =========================

async def send_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):

    path = context.user_data.get("path", [])

    current_node = get_node(path)

    keyboard = []

    # =========================
    # HOME
    # =========================

    if not path:

        for level in STRUCTURE:
            keyboard.append([
                KeyboardButton(level)
            ])

    # =========================
    # CURRENT NODE
    # =========================

    elif isinstance(current_node, dict):

        for item in current_node:
            keyboard.append([
                KeyboardButton(item)
            ])

    # =========================
    # SUBJECT
    # =========================

    elif isinstance(current_node, list):

        keyboard.append([
            KeyboardButton("📚 Theoretical")
        ])

        keyboard.append([
            KeyboardButton("🧪 Practical")
        ])

    # =========================
    # BACK
    # =========================

    if path:
        keyboard.append([
            KeyboardButton("🔙 Back")
        ])

    # =========================
    # ADMIN DELETE
    # =========================

    user = update.effective_user

    if user and is_admin(user.id):
        keyboard.append([
            KeyboardButton("🗑️ Delete File")
        ])

    reply_markup = ReplyKeyboardMarkup(
        keyboard,
        resize_keyboard=True
    )

    # =========================
    # SEND MENU
    # =========================

    await update.message.reply_text(
        "📚 Choose:",
        reply_markup=reply_markup
    )

    # =========================
    # SHOW FILES
    # =========================

    path_key = get_current_path_key(path)

    files = file_database.get(path_key, [])

    if files:

        file_keyboard = []

        for file_info in files:

            icon = get_file_icon(file_info["type"])

            file_keyboard.append([
                InlineKeyboardButton(
                    f"{icon} {file_info['name']}",
                    callback_data=f"FILE:{file_info['key']}"
                )
            ])

        await update.message.reply_text(
            "📂 Files:",
            reply_markup=InlineKeyboardMarkup(file_keyboard)
        )


# =========================
# FILE CALLBACK
# =========================

async def handle_file_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    data = query.data

    if not data.startswith("FILE:"):
        return

    file_key = data.replace("FILE:", "", 1)

    file_info = None

    # =========================
    # SEARCH FOR FILE
    # =========================

    for path_key, files in file_database.items():

        for f in files:

            if f.get("key") == file_key:
                file_info = f
                break

        if file_info:
            break

    # =========================
    # FILE NOT FOUND
    # =========================

    if not file_info:

        await query.message.reply_text(
            "❌ الملف مش موجود أو تم حذفه."
        )

        return

    try:

        # =========================
        # COPY ORIGINAL MESSAGE
        # =========================

        await context.bot.copy_message(
            chat_id=query.message.chat_id,
            from_chat_id=file_info["chat_id"],
            message_id=file_info["message_id"]
        )

    except Exception as e:

        logger.error(
            "Error copying file: %s",
            e
        )

        await query.message.reply_text(
            "❌ حصل خطأ أثناء فتح الملف."
        )


# =========================
# HANDLE NORMAL MESSAGES
# =========================

async def handle_message(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    if not update.message:
        return

    text = update.message.text

    if not text:
        return

    user = update.effective_user

    path = context.user_data.get("path", [])

    # =========================
    # HOME
    # =========================

    if text == "🏠 Home":

        context.user_data["path"] = []
        context.user_data["deleting_mode"] = False

        await send_menu(update, context)

        return

    # =========================
    # BACK
    # =========================

    if text == "🔙 Back":

        if path:
            path.pop()

        context.user_data["path"] = path
        context.user_data["deleting_mode"] = False

        await send_menu(update, context)

        return

    # =========================
    # DELETE MODE
    # =========================

    if text == "🗑️ Delete File":

        if not is_admin(user.id):

            await update.message.reply_text(
                "❌ You are not an admin."
            )

            return

        path_key = get_current_path_key(path)

        files = file_database.get(path_key, [])

        if not files:

            await update.message.reply_text(
                "❌ No files here."
            )

            return

        context.user_data["deleting_mode"] = True

        delete_keyboard = []

        for f in files:

            icon = get_file_icon(f["type"])

            delete_keyboard.append([
                KeyboardButton(
                    f"❌ {icon} {f['name']}"
                )
            ])

        delete_keyboard.append([
            KeyboardButton("🔙 Back")
        ])

        await update.message.reply_text(
            "🗑️ Choose the file you want to delete:",
            reply_markup=ReplyKeyboardMarkup(
                delete_keyboard,
                resize_keyboard=True
            )
        )

        return

    # =========================
    # DELETE FILE
    # =========================

    if (
        context.user_data.get("deleting_mode")
        and is_admin(user.id)
        and text.startswith("❌ ")
    ):

        file_name = text[2:].strip()

        path_key = get_current_path_key(path)

        files = file_database.get(path_key, [])

        for f in files:

            icon = get_file_icon(f["type"])

            if f"❌ {icon} {f['name']}" == text:

                files.remove(f)

                await update.message.reply_text(
                    f"✅ Deleted: {f['name']}"
                )

                break

        context.user_data["deleting_mode"] = False

        await send_menu(update, context)

        return

    # =========================
    # NAVIGATION
    # =========================

    current_node = get_node(path)

    # =========================
    # DICTIONARY
    # =========================

    if isinstance(current_node, dict):

        if text in current_node:

            path.append(text)

            context.user_data["path"] = path

            await send_menu(update, context)

            return

    # =========================
    # LIST / SUBJECT
    # =========================

    elif isinstance(current_node, list):

        if text in [
            "📚 Theoretical",
            "🧪 Practical"
        ]:

            path.append(text)

            context.user_data["path"] = path

            await send_menu(update, context)

            return

    # =========================
    # UNKNOWN
    # =========================

    await update.message.reply_text(
        "❌ Choose something from the buttons."
    )


# =========================
# HANDLE FILE UPLOAD
# =========================

async def handle_media_upload(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user = update.effective_user

    # =========================
    # ADMIN ONLY
    # =========================

    if not is_admin(user.id):

        await update.message.reply_text(
            "❌ Only admins can upload files."
        )

        return

    path = context.user_data.get("path", [])

    path_key = get_current_path_key(path)

    # =========================
    # DETECT FILE TYPE
    # =========================

    file_type = None
    file_name = None

    if update.message.document:

        file_type = "document"

        file_name = (
            update.message.document.file_name
            or "Unnamed Document"
        )

    elif update.message.photo:

        file_type = "photo"

        file_name = "Photo"

    elif update.message.audio:

        file_type = "audio"

        file_name = (
            update.message.audio.file_name
            or "Audio"
        )

    elif update.message.voice:

        file_type = "voice"

        file_name = "Voice Message"

    else:

        return

    # =========================
    # CREATE PATH
    # =========================

    if path_key not in file_database:

        file_database[path_key] = []

    # =========================
    # UNIQUE KEY
    # =========================

    file_key = uuid.uuid4().hex[:16]

    # =========================
    # SAVE ORIGINAL MESSAGE
    # =========================

    file_database[path_key].append({

        "key": file_key,

        "name": file_name,

        "type": file_type,

        "chat_id": update.effective_chat.id,

        "message_id": update.message.message_id,
    })

    # =========================
    # CONFIRM
    # =========================

    await update.message.reply_text(
        f"✅ Saved successfully!\n\n"
        f"📁 Location:\n{path_key}\n\n"
        f"📄 File:\n{
