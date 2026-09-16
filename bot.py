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

BOT_TOKEN = os.getenv("BOT_TOKEN", "8791458947:AAFqU8dMWrO3Ov5JjDWMv4OqrIXSZdmaPIY")
ADMIN_IDS = [6448008082, 8791458947]

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

STRUCTURE = {
    "🔴 Level 1": {
        "Semester 1": {
            "🦴 Anatomy I": {"type": "subject", "lab": True},
            "🧪 Biochemistry I": {"type": "subject", "lab": False},
            "🔬 Histology": {"type": "subject", "lab": True},
            "🫀 Physiology I": {"type": "subject", "lab": True}
        },
        "Semester 2": {
            "🦴 Anatomy II": {"type": "subject", "lab": True},
            "🧪 Biochemistry II": {"type": "subject", "lab": False},
            "🫀 Physiology II": {"type": "subject", "lab": True},
            "🏃 Kinesiology I": {"type": "subject", "lab": True},
            "⚡ Biophysics": {"type": "subject", "lab": True}
        }
    },
    "🟠 Level 2": {
        "Semester 3": {
            "🧠 Neuroanatomy": {"type": "subject", "lab": True},
            "🦾 Biomechanics II": {"type": "subject", "lab": True},
            "⚡ Electrotherapy I": {"type": "subject", "lab": True},
            "📋 Evaluation I": {"type": "subject", "lab": True},
            "🧠 Neurophysiology": {"type": "subject", "lab": False},
            "🏋️ Therapeutic Ex. I": {"type": "subject", "lab": True}
        },
        "Semester 4": {
            "🦾 Biomechanics III": {"type": "subject", "lab": True},
            "🩺 Community Health": {"type": "subject", "lab": False},
            "📋 Evaluation II": {"type": "subject", "lab": True},
            "🫀 Exercise Physiology": {"type": "subject", "lab": False},
            "🔬 Pathology": {"type": "subject", "lab": False},
            "👐 Manual Therapy": {"type": "subject", "lab": True},
            "⚡ Electrotherapy II": {"type": "subject", "lab": True},
            "🦴 Anatomy IV": {"type": "subject", "lab": True},
            "⚖️ Legal & Ethics": {"type": "subject", "lab": False}
        }
    },
    "🟡 Level 3": {
        "Semester 5": {
            "🦾 Biomechanics IV": {"type": "subject", "lab": True},
            "🌊 Hydrotherapy": {"type": "subject", "lab": True},
            "📊 Research & Statistics": {"type": "subject", "lab": False},
            "💼 Management & Decision": {"type": "subject", "lab": False},
            "🩺 Pathophysiology": {"type": "subject", "lab": False},
            "💊 Pharmacology": {"type": "subject", "lab": False},
            "♿ Rehabilitation": {"type": "subject", "lab": False}
        }
    },
    "🟢 Tracks": {
        "🫀 Batna Track": {
            "🩺 Clin. Med. Cardio": {"type": "subject", "lab": False},
            "🫁 Clin. Med. Chest & Internal": {"type": "subject", "lab": False},
            "👵 Clin. Practice Geriatrics": {"type": "subject", "lab": True},
            "🫀 Clin. Practice Cardio & Pulm.": {"type": "subject", "lab": True},
            "🦯 Geriatric Rehab": {"type": "subject", "lab": True},
            "🫁 P.T. Chest & Internal": {"type": "subject", "lab": True},
            "🫀 P.T. Cardio": {"type": "subject", "lab": True},
            "🥗 Nutrition": {"type": "subject", "lab": False},
            "🧠 Psych. for Handicapped": {"type": "subject", "lab": False},
            "🩻 Radiology": {"type": "subject", "lab": False}
        },
        "🤰 Gyna Track": {
            "🪑 Ergonomics": {"type": "subject", "lab": True},
            "🩺 Clin. Practice Surgery": {"type": "subject", "lab": True},
            "🩹 P.T. Surgery": {"type": "subject", "lab": True},
            "👩‍⚕️ Clin. Practice Womens Health": {"type": "subject", "lab": True},
            "🤰 P.T. Womens Health": {"type": "subject", "lab": True},
            "🩺 Clin. Med. Womens Health": {"type": "subject", "lab": False},
            "📚 Evidence Based Practice": {"type": "subject", "lab": False},
            "🏥 General Surgery & ICU": {"type": "subject", "lab": False}
        },
        "🦴 Ortho Track": {
            "🩺 Clin. Med. Traumatology": {"type": "subject", "lab": False},
            "🦴 Clin. Med. Ortho Surgery": {"type": "subject", "lab": False},
            "📋 Physical Diagnosis": {"type": "subject", "lab": True},
            "🦴 P.T. Orthopedics": {"type": "subject", "lab": True},
            "🦿 Orthotics & Prosthetics": {"type": "subject", "lab": True},
            "🩻 Radiodiagnosis": {"type": "subject", "lab": False},
            "⚽ Sport P.T.": {"type": "subject", "lab": True},
            "🏥 Clin. Practice Ortho": {"type": "subject", "lab": True}
        },
        "👶 Peds Track": {
            "🩺 Clin. Med. Pediatrics": {"type": "subject", "lab": False},
            "👶 Clin. Practice Peds": {"type": "subject", "lab": True},
            "🧸 Motor Development": {"type": "subject", "lab": True},
            "👶 P.T. Pediatrics": {"type": "subject", "lab": True},
            "🏥 P.T. Pediatric Surgery": {"type": "subject", "lab": True},
            "🗣️ Speech Therapy": {"type": "subject", "lab": False},
            "🧩 Occupational Therapy": {"type": "subject", "lab": False}
        },
        "🧠 Neuro Track": {
            "🩺 Clin. Med. Neurology": {"type": "subject", "lab": False},
            "🧠 Clin. Practice Neuro": {"type": "subject", "lab": True},
            "🧠 P.T. Neurology": {"type": "subject", "lab": True},
            "🔪 P.T. Neurosurgery": {"type": "subject", "lab": True},
            "🏥 Neurosurgery": {"type": "subject", "lab": False},
            "🔬 Recent Neuro Rehab": {"type": "subject", "lab": True},
            "⚡ Electrodiagnosis": {"type": "subject", "lab": True},
            "🏃 Motor Learning": {"type": "subject", "lab": False}
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

    if isinstance(current_node, dict):
        if current_node.get("type") == "subject":
            if current_node.get("lab"):
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

    path_key = " -> ".join(path) if path else "Root (Home)"
    files = file_database.get(path_key, [])

    if files:
        for f in files:
            icon = "📄" if f["type"] == "document" else ("🖼️" if f["type"] == "photo" else "🎙️")
            keyboard.append([KeyboardButton(f"{icon} {f['name']}")])

    control_row = []
    if path:
        control_row.append(KeyboardButton("Back"))
        control_row.append(KeyboardButton("Home"))

    if control_row:
        keyboard.append(control_row)

    if len(files) > 0 and is_admin(update.effective_user.id):
        keyboard.append([KeyboardButton("Delete File")])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    msg_text = f"{text}\n\n📍 Current Location: {path_key}"
    if not files:
        msg_text += "\n\n📂 No files uploaded in this location yet."

    if is_admin(update.effective_user.id):
        msg_text += "\n\n⚙️ [Admin Mode]: Send any PDF, Image, or Audio to save it right here!"

    # تم حذف parse_mode لتسهيل وقبول جميع الرموز والأقواس بدون كراش
    await update.message.reply_text(msg_text, reply_markup=reply_markup)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text.strip()
    
    if "path" not in context.user_data:
        context.user_data["path"] = []
    path = context.user_data["path"]
    user_id = update.effective_user.id

    if text in ["Home", "/start"]:
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
            await update.message.reply_text("⚠️ No files available to delete!")
            return
        
        context.user_data["deleting_mode"] = True
        delete_keyboard = []
        for i in range(0, len(files), 2):
            row = [KeyboardButton(f"Delete: {files[i]['name']}")]
            if i + 1 < len(files):
                row.append(KeyboardButton(f"Delete: {files[i+1]['name']}"))
            delete_keyboard.append(row)
        delete_keyboard.append([KeyboardButton("Back"), KeyboardButton("Home")])
        
        await update.message.reply_text("Select file to delete:", reply_markup=ReplyKeyboardMarkup(delete_keyboard, resize_keyboard=True))
        return

    if text.startswith("Delete: ") and context.user_data.get("deleting_mode"):
        file_to_delete = text.replace("Delete: ", "")
        path_key = " -> ".join(path) if path else "Root (Home)"
        file_database[path_key] = [f for f in file_database.get(path_key, []) if f["name"] != file_to_delete]
        context.user_data["deleting_mode"] = False
        await update.message.reply_text(f"🗑️ Deleted: {file_to_delete}")
        await send_menu(update, context, "Updated list:")
        return

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
            if key.strip() == text and key not in ["type", "lab"]:
                matched_key = key
                break

    if matched_key:
        item = current_node[matched_key]
        path.append(matched_key)
        context.user_data["path"] = path

        if isinstance(item, dict) and item.get("type") == "subject":
            keyboard = []
            if item.get("lab"):
                keyboard.append([KeyboardButton("Theoretical"), KeyboardButton("Practical")])
            else:
                keyboard.append([KeyboardButton("Theoretical")])
            keyboard.append([KeyboardButton("Back"), KeyboardButton("Home")])
            
            await update.message.reply_text(f"Select component for {matched_key}:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
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
        file_name = update.message.caption or f"Photo_{len(file_database[path_key])+1}.jpg"
        file_type = "photo"
    elif update.message.voice or update.message.audio:
        media = update.message.voice or update.message.audio
        file_id = media.file_id
        file_name = update.message.caption or f"Audio_{len(file_database[path_key])+1}.mp3"
        file_type = "audio"
    else:
        return

    file_database[path_key].append({
        "name": file_name,
        "file_id": file_id,
        "type": file_type
    })

    await update.message.reply_text(f"✅ Saved {file_name} to {path_key}!")
    await send_menu(update, context, "Updated Folder Status:")

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    
    media_filter = filters.Document.ALL | filters.PHOTO | filters.VOICE | filters.AUDIO
    app.add_handler(MessageHandler(media_filter, handle_media_upload))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot running smoothly...")
    app.run_polling()
                            
