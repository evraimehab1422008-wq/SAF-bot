import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# Token configuration and Admin list
BOT_TOKEN = os.getenv("BOT_TOKEN", "8791458947:AAG2A5K0soKYuahev0439Ixg0yiHehaJ9MQ")
ADMIN_IDS = [6448008082, 8791458947]

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

STRUCTURE = {
    "🔴 Level 1": {
        "Semester 1": {
            "🦴 Anatomy I": {"has_lab": True},
            "🧪 Biochemistry I": {"has_lab": False},
            "🔬 Histology": {"has_lab": True},
            "🫀 Physiology I": {"has_lab": True}
        },
        "Semester 2": {
            "🦴 Anatomy II": {"has_lab": True},
            "🧪 Biochemistry II": {"has_lab": False},
            "🫀 Physiology II": {"has_lab": True},
            "🏃 Kinesiology I": {"has_lab": True},
            "⚡ Biophysics": {"has_lab": True}
        }
    },
    "🟠 Level 2": {
        "Semester 3": {
            "🧠 Neuroanatomy": {"has_lab": True},
            "🦾 Biomechanics II": {"has_lab": True},
            "⚡ Electrotherapy I": {"has_lab": True},
            "📋 Evaluation I": {"has_lab": True},
            "🧠 Neurophysiology": {"has_lab": False},
            "🏋️ Therapeutic Ex. I": {"has_lab": True}
        },
        "Semester 4": {
            "🦾 Biomechanics III": {"has_lab": True},
            "🩺 Community Health": {"has_lab": False},
            "📋 Evaluation II": {"has_lab": True},
            "🫀 Exercise Physiology": {"has_lab": False},
            "🔬 Pathology": {"has_lab": False},
            "👐 Manual Therapy": {"has_lab": True},
            "⚡ Electrotherapy II": {"has_lab": True},
            "🦴 Anatomy IV": {"has_lab": True},
            "⚖️ Legal & Ethics": {"has_lab": False}
        }
    },
    "🟡 Level 3": {
        "Semester 5": {
            "🦾 Biomechanics IV": {"has_lab": True},
            "🌊 Hydrotherapy": {"has_lab": True},
            "📊 Research & Statistics": {"has_lab": False},
            "💼 Management & Decision": {"has_lab": False},
            "🩺 Pathophysiology": {"has_lab": False},
            "💊 Pharmacology": {"has_lab": False},
            "♿ Rehabilitation": {"has_lab": False}
        }
    },
    "🟢 Tracks": {
        "🫀 Batna Track": {
            "🩺 Clin. Med. Cardio": {"has_lab": False},
            "🫁 Clin. Med. Chest & Internal": {"has_lab": False},
            "👵 Clin. Practice Geriatrics": {"has_lab": True},
            "🫀 Clin. Practice Cardio & Pulm.": {"has_lab": True},
            "🦯 Geriatric Rehab": {"has_lab": True},
            "🫁 P.T. Chest & Internal": {"has_lab": True},
            "🫀 P.T. Cardio": {"has_lab": True},
            "🥗 Nutrition": {"has_lab": False},
            "🧠 Psych. for Handicapped": {"has_lab": False},
            "🩻 Radiology": {"has_lab": False}
        },
        "🤰 Gyna Track": {
            "🪑 Ergonomics": {"has_lab": True},
            "🩺 Clin. Practice Surgery": {"has_lab": True},
            "🩹 P.T. Surgery": {"has_lab": True},
            "👩‍⚕️ Clin. Practice Womens Health": {"has_lab": True},
            "🤰 P.T. Womens Health": {"has_lab": True},
            "🩺 Clin. Med. Womens Health": {"has_lab": False},
            "📚 Evidence Based Practice": {"has_lab": False},
            "🏥 General Surgery & ICU": {"has_lab": False}
        },
        "🦴 Ortho Track": {
            "🩺 Clin. Med. Traumatology": {"has_lab": False},
            "🦴 Clin. Med. Ortho Surgery": {"has_lab": False},
            "📋 Physical Diagnosis": {"has_lab": True},
            "🦴 P.T. Orthopedics": {"has_lab": True},
            "🦿 Orthotics & Prosthetics": {"has_lab": True},
            "🩻 Radiodiagnosis": {"has_lab": False},
            "⚽ Sport P.T.": {"has_lab": True},
            "🏥 Clin. Practice Ortho": {"has_lab": True}
        },
        "👶 Peds Track": {
            "🩺 Clin. Med. Pediatrics": {"has_lab": False},
            "👶 Clin. Practice Peds": {"has_lab": True},
            "🧸 Motor Development": {"has_lab": True},
            "👶 P.T. Pediatrics": {"has_lab": True},
            "🏥 P.T. Pediatric Surgery": {"has_lab": True},
            "🗣️ Speech Therapy": {"has_lab": False},
            "🧩 Occupational Therapy": {"has_lab": False}
        },
        "🧠 Neuro Track": {
            "🩺 Clin. Med. Neurology": {"has_lab": False},
            "🧠 Clin. Practice Neuro": {"has_lab": True},
            "🧠 P.T. Neurology": {"has_lab": True},
            "🔪 P.T. Neurosurgery": {"has_lab": True},
            "🏥 Neurosurgery": {"has_lab": False},
            "🔬 Recent Neuro Rehab": {"has_lab": True},
            "⚡ Electrodiagnosis": {"has_lab": True},
            "🏃 Motor Learning": {"has_lab": False}
        }
    }
}

file_database = {}

def get_node(path):
    current = STRUCTURE
    for p in path:
        if isinstance(current, dict) and p in current:
            current = current[p]
        else:
            return None
    return current

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["path"] = []
    context.user_data["deleting_mode"] = False
    await send_menu(update, context, "Welcome to Physical Therapy Academic Bot 🩺\nSelect a section:")

async def send_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    path = context.user_data.get("path", [])
    current_node = get_node(path)

    keyboard = []

    # 1. إضافة أزرار الأقسام أو خيارات Theoretical/Practical
    if isinstance(current_node, dict):
        if "has_lab" in current_node:
            if current_node["has_lab"]:
                keyboard.append([KeyboardButton("Theoretical"), KeyboardButton("Practical")])
            else:
                keyboard.append([KeyboardButton("Theoretical")])
        else:
            keys = list(current_node.keys())
            for i in range(0, len(keys), 2):
                row = [KeyboardButton(keys[i])]
                if i + 1 < len(keys):
                    row.append(KeyboardButton(keys[i+1]))
                keyboard.append(row)

    # 2. تحويل الملفات المرفوعة لأزرار قابلة للضغط!
    path_key = " -> ".join(path) if path else "Root (Home)"
    files = file_database.get(path_key, [])

    if files:
        for f in files:
            icon = "📄" if f["type"] == "document" else ("🖼️" if f["type"] == "photo" else "🎙️")
            keyboard.append([KeyboardButton(f"{icon} {f['name']}")])

    # 3. أزرار التحكم
    control_row = []
    if path:
        control_row.append(KeyboardButton("Back"))
        control_row.append(KeyboardButton("Home"))

    if control_row:
        keyboard.append(control_row)

    if len(files) > 0 and is_admin(update.effective_user.id):
        keyboard.append([KeyboardButton("Delete File")])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    msg_text = text + f"\n\n📍 **Current Location:** `{path_key}`"
    if files:
        msg_text += "\n\n📚 **Click any file below to download/view it:**"
    else:
        msg_text += "\n\n📂 No files uploaded in this location yet."

    if is_admin(update.effective_user.id):
        msg_text += "\n\n⚙️ **[Admin Mode]:** Send any PDF, Image, or Audio to save it right here!"

    await update.message.reply_text(msg_text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if "path" not in context.user_data:
        context.user_data["path"] = []
    path = context.user_data["path"]
    user_id = update.effective_user.id

    if text == "Home":
        context.user_data["path"] = []
        context.user_data["deleting_mode"] = False
        await send_menu(update, context, "Home Menu:")
        return

    if text == "Back":
        if path:
            path.pop()
            context.user_data["path"] = path
        context.user_data["deleting_mode"] = False
        await send_menu(update, context, "Navigating back:")
        return

    if text == "Delete File":
        if not is_admin(user_id):
            return
        path_key = " -> ".join(path) if path else "Root (Home)"
        files = file_database.get(path_key, [])
        if not files:
            await update.message.reply_text("⚠️ No files available to delete in this section!")
            return
        
        context.user_data["deleting_mode"] = True
        delete_keyboard = []
        for i in range(0, len(files), 2):
            row = [KeyboardButton(f"Delete: {files[i]['name']}")]
            if i + 1 < len(files):
                row.append(KeyboardButton(f"Delete: {files[i+1]['name']}"))
            delete_keyboard.append(row)
        delete_keyboard.append([KeyboardButton("Back"), KeyboardButton("Home")])
        
        await update.message.reply_text("Select the file you want to delete:", reply_markup=ReplyKeyboardMarkup(delete_keyboard, resize_keyboard=True))
        return

    if text.startswith("Delete: ") and context.user_data.get("deleting_mode"):
        file_to_delete = text.replace("Delete: ", "")
        path_key = " -> ".join(path) if path else "Root (Home)"
        file_database[path_key] = [f for f in file_database.get(path_key, []) if f["name"] != file_to_delete]
        context.user_data["deleting_mode"] = False
        await update.message.reply_text(f"🗑️ Successfully deleted: `{file_to_delete}`", parse_mode="Markdown")
        await send_menu(update, context, "Updated list:")
        return

    # التحقق هل المستخدم داس على زرار ملف ليرسله له البوت
    path_key = " -> ".join(path) if path else "Root (Home)"
    files = file_database.get(path_key, [])
    for f in files:
        if f["name"] in text:
            if f["type"] == "document":
                await update.message.reply_document(document=f["file_id"])
            elif f["type"] == "photo":
                await update.message.reply_photo(photo=f["file_id"])
            elif f["type"] == "audio":
                await update.message.reply_audio(audio=f["file_id"])
            return

    current_node = get_node(path)

    matched_key = None
    if isinstance(current_node, dict):
        for key in current_node.keys():
            if key.strip() == text and key != "has_lab":
                matched_key = key
                break

    if matched_key:
        item = current_node[matched_key]
        path.append(matched_key)
        context.user_data["path"] = path

        if isinstance(item, dict) and "has_lab" in item:
            keyboard = []
            if item["has_lab"]:
                keyboard.append([KeyboardButton("Theoretical"), KeyboardButton("Practical")])
            else:
                keyboard.append([KeyboardButton("Theoretical")])
            keyboard.append([KeyboardButton("Back"), KeyboardButton("Home")])
            
            await update.message.reply_text(f"Select component for ({matched_key}):", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
            return
        else:
            await send_menu(update, context, f"Selected: {matched_key}")
            return

    if text in ["Theoretical", "Practical"]:
        path.append(text)
        context.user_data["path"] = path
        await send_menu(update, context, f"Section: {text}")
        return

async def handle_media_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return

    if "path" not in context.user_data:
        context.user_data["path"] = []
        
    path = context.user_data["path"]
    path_key = " -> ".join(path) if path else "Root (Home)"

    if path_key not in file_database:
        file_database[path_key] = []

    if update.message.document:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name or "PDF File"
        file_type = "document"
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_name = update.message.caption or f"Image_{len(file_database[path_key])+1}"
        file_type = "photo"
    elif update.message.voice or update.message.audio:
        media = update.message.voice or update.message.audio
        file_id = media.file_id
        file_name = update.message.caption or f"Audio_{len(file_database[path_key])+1}"
        file_type = "audio"
    else:
        return

    file_database[path_key].append({
        "name": file_name,
        "file_id": file_id,
        "type": file_type
    })

    await update.message.reply_text(f"✅ Successfully uploaded `{file_name}` to `{path_key}`!", parse_mode="Markdown")
    await send_menu(update, context, "File stored. Here are the updated buttons:")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    
    media_filter = filters.Document.ALL | filters.PHOTO | filters.VOICE | filters.AUDIO
    app.add_handler(MessageHandler(media_filter, handle_media_upload))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot is running...")
    app.run_polling()
    
