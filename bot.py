import os
import json
import logging
import time
import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

TOKEN = "8791458947:AAG-CJRYAPiixXNretthMePindhMOhBdfIo"
ADMIN_IDS = [6448008082]
DATA_FILE = "data.json"

def clean_text(text):
    return re.sub(r'[^\w\s\(\)\/-]', '', text).strip()

def load_data():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_data(data):
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

MAIN_MENU = [
    [KeyboardButton("Level 1 🟢"), KeyboardButton("Level 2 🟡")],
    [KeyboardButton("Level 3 🟠"), KeyboardButton("Level 4 🔴")],
    [KeyboardButton("Level 5 🟣")]
]

LEVEL_1_MENU = [
    [KeyboardButton("Semester 1"), KeyboardButton("Semester 2")],
    [KeyboardButton("🔙 Back")]
]

LEVEL_2_MENU = [
    [KeyboardButton("Semester 3"), KeyboardButton("Semester 4")],
    [KeyboardButton("🔙 Back")]
]

LEVEL_3_MENU = [
    [KeyboardButton("Semester 5"), KeyboardButton("Semester 6 (Batna term)")],
    [KeyboardButton("🔙 Back")]
]

LEVEL_4_MENU = [
    [KeyboardButton("Semester 7 (Gyna term)"), KeyboardButton("Semester 8 (Ortho term)")],
    [KeyboardButton("🔙 Back")]
]

LEVEL_5_MENU = [
    [KeyboardButton("Paediatric term (children)"), KeyboardButton("Neuro term (Semester 10)")],
    [KeyboardButton("🔙 Back")]
]

SUBJECTS = {
    "Semester 1": ["💀 Human Anatomy I", "🧪 Biochemistry I", "🔬 Histology", "🫀 Human Physiology I"],
    "Semester 2": ["💀 Human Anatomy II", "🧪 Biochemistry II", "🫀 Human Physiology II", "🦵 Kinesiology I", "⚡ Biophysics II"],
    "Semester 3": ["🧠 Human Anatomy III (Neuroanatomy)", "⚙️ Biomechanics II", "🔌 Electrotherapy I", "📏 Evaluation/Measurements I", "🧠 Human Physiology III (Neurophysiology)", "🏋️ Therapeutic Exercises I"],
    "Semester 4": ["⚙️ Biomechanics III", "🏛️ Community Health and Hygiene", "📏 Evaluation/Measurements II", "🏃 Physiology IV (Exercise Physiology)", "🦠 Pathology for Physical Therapy", "👐 Manual Therapy", "🔌 Electrotherapy II", "💀 Human Anatomy IV", "⚖️ Legal and Ethical Issues in Physiotherapy"],
    "Semester 5": ["⚙️ Biomechanics IV", "🌊 Hydrotherapy", "📊 Research and Medical Statistics", "📋 Management and Clinical Decision", "🩸 Pathophysiology", "💊 Pharmacology for Physical Therapy", "♿ Rehabilitation"],
    "Semester 6 (Batna term)": ["❤️ Clinical Medicine for Cardiovascular Conditions", "🫁 Clinical Medicine for Pulmonary and Internal Conditions", "👴 Clinical Practice for Geriatrics", "🫁 Clinical Practice for Cardiovascular and Pulmonary Disorders", "👴 Geriatric Rehabilitation", "🫁 Physical Therapy for Pulmonary and Internal Conditions", "❤️ Physical Therapy for Cardiovascular Disorders", "🥗 Clinical Nutrition", "🧠 Psychology for Handicapped", "🩻 Radiology"],
    "Semester 7 (Gyna term)": ["🪑 Ergonomics", "🩺 Clinical Practice for Integumentary and Surgical Conditions", "🩹 Physical Therapy for Integumentary and Surgical Conditions", "🤰 Clinical Practice for Women Health", "🤰 Physical Therapy for Women Health", "🤰 Clinical Medicine for Women Health", "📚 Evidence Based Practice", "🔪 General Surgery and Intensive Care"],
    "Semester 8 (Ortho term)": ["🦴 Clinical Medicine for Traumatology", "🦴 Clinical Medicine for Orthopedic Surgery", "🔍 Physical Diagnosis and Examination", "🦴 Physical Therapy for Orthopedics", "🦿 Orthotics and Prosthetics", "🩻 Radiodiagnosis", "⚽ Sport Physical Therapy", "🦴 Clinical Practice for Traumatology and Orthopedic Surgery"],
    "Paediatric term (children)": ["👶 Clinical Medicine for Pediatrics and Surgical Cases", "👶 Clinical Practice for Pediatrics and Surgical Cases", "🌱 Motor Development Across Life Span", "👶 Physical Therapy for Pediatrics", "👶 Physical Therapy for Pediatric Surgical Conditions", "🗣️ Speech Therapy", "🎨 Occupational Therapy"],
    "Neuro term (Semester 10)": ["🧠 Clinical Medicine for Neurology", "🧠 Clinical Practice for Neurological and Neurosurgical Conditions", "🧠 Physical Therapy for Neurological Conditions", "🧠 Physical Therapy for Neurosurgical Conditions", "🧠 Neurosurgery", "🧠 Recent Approaches in Neurological Rehabilitation", "⚡ Electrodiagnosis", "🚶 Motor Learning and Control"]
}

TYPES = {
    "Human Anatomy I": ["Theoretical 📖", "Practical 🔬"], "Biochemistry I": ["Theoretical 📖"], "Histology": ["Theoretical 📖", "Practical 🔬"], "Human Physiology I": ["Theoretical 📖", "Practical 🔬"],
    "Human Anatomy II": ["Theoretical 📖", "Practical 🔬"], "Biochemistry II": ["Theoretical 📖"], "Human Physiology II": ["Theoretical 📖", "Practical 🔬"], "Kinesiology I": ["Theoretical 📖", "Practical 🔬"], "Biophysics II": ["Theoretical 📖", "Practical 🔬"],
    "Human Anatomy III (Neuroanatomy)": ["Theoretical 📖", "Practical 🔬"], "Biomechanics II": ["Theoretical 📖", "Practical 🔬"], "Electrotherapy I": ["Theoretical 📖", "Practical 🔬"], "Evaluation/Measurements I": ["Theoretical 📖", "Practical 🔬"], "Human Physiology III (Neurophysiology)": ["Theoretical 📖"], "Therapeutic Exercises I": ["Theoretical 📖", "Practical 🔬"],
    "Biomechanics III": ["Theoretical 📖", "Practical 🔬"], "Community Health and Hygiene": ["Theoretical 📖"], "Evaluation/Measurements II": ["Theoretical 📖", "Practical 🔬"], "Physiology IV (Exercise Physiology)": ["Theoretical 📖"], "Pathology for Physical Therapy": ["Theoretical 📖"], "Manual Therapy": ["Theoretical 📖", "Practical 🔬"], "Electrotherapy II": ["Theoretical 📖", "Practical 🔬"], "Human Anatomy IV": ["Theoretical 📖", "Practical 🔬"], "Legal and Ethical Issues in Physiotherapy": ["Theoretical 📖"],
    "Biomechanics IV": ["Theoretical 📖", "Practical 🔬"], "Hydrotherapy": ["Theoretical 📖", "Practical 🔬"], "Research and Medical Statistics": ["Theoretical 📖"], "Management and Clinical Decision": ["Theoretical 📖"], "Pathophysiology": ["Theoretical 📖"], "Pharmacology for Physical Therapy": ["Theoretical 📖"], "Rehabilitation": ["Theoretical 📖"],
    "Clinical Medicine for Cardiovascular Conditions": ["Theoretical 📖"], "Clinical Medicine for Pulmonary and Internal Conditions": ["Theoretical 📖"], "Clinical Practice for Geriatrics": ["Practical 🔬"], "Clinical Practice for Cardiovascular and Pulmonary Disorders": ["Practical 🔬"], "Geriatric Rehabilitation": ["Theoretical 📖", "Practical 🔬"], "Physical Therapy for Pulmonary and Internal Conditions": ["Theoretical 📖", "Practical 🔬"], "Physical Therapy for Cardiovascular Disorders": ["Theoretical 📖", "Practical 🔬"], "Clinical Nutrition": ["Theoretical 📖"], "Psychology for Handicapped": ["Theoretical 📖"], "Radiology": ["Theoretical 📖"],
    "Ergonomics": ["Theoretical 📖", "Practical 🔬"], "Clinical Practice for Integumentary and Surgical Conditions": ["Practical 🔬"], "Physical Therapy for Integumentary and Surgical Conditions": ["Theoretical 📖", "Practical 🔬"], "Clinical Practice for Women Health": ["Practical 🔬"], "Physical Therapy for Women Health": ["Theoretical 📖", "Practical 🔬"], "Clinical Medicine for Women Health": ["Theoretical 📖"], "Evidence Based Practice": ["Theoretical 📖"], "General Surgery and Intensive Care": ["Theoretical 📖"],
    "Clinical Medicine for Traumatology": ["Theoretical 📖"], "Clinical Medicine for Orthopedic Surgery": ["Theoretical 📖"], "Physical Diagnosis and Examination": ["Theoretical 📖", "Practical 🔬"], "Physical Therapy for Orthopedics": ["Theoretical 📖", "Practical 🔬"], "Orthotics and Prosthetics": ["Theoretical 📖", "Practical 🔬"], "Radiodiagnosis": ["Theoretical 📖"], "Sport Physical Therapy": ["Theoretical 📖", "Practical 🔬"], "Clinical Practice for Traumatology and Orthopedic Surgery": ["Practical 🔬"],
    "Clinical Medicine for Pediatrics and Surgical Cases": ["Theoretical 📖"], "Clinical Practice for Pediatrics and Surgical Cases": ["Practical 🔬"], "Motor Development Across Life Span": ["Theoretical 📖"], "Physical Therapy for Pediatrics": ["Theoretical 📖", "Practical 🔬"], "Physical Therapy for Pediatric Surgical Conditions": ["Theoretical 📖", "Practical 🔬"], "Speech Therapy": ["Theoretical 📖"], "Occupational Therapy": ["Theoretical 📖"],
    "Clinical Medicine for Neurology": ["Theoretical 📖"], "Clinical Practice for Neurological and Neurosurgical Conditions": ["Practical 🔬"], "Physical Therapy for Neurological Conditions": ["Theoretical 📖", "Practical 🔬"], "Physical Therapy for Neurosurgical Conditions": ["Theoretical 📖", "Practical 🔬"], "Neurosurgery": ["Theoretical 📖"], "Recent Approaches in Neurological Rehabilitation": ["Theoretical 📖", "Practical 🔬"], "Electrodiagnosis": ["Theoretical 📖", "Practical 🔬"], "Motor Learning and Control": ["Theoretical 📖"]
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['stack'] = []
    reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
    await update.message.reply_text("Welcome! Select Level:", reply_markup=reply_markup)

async def handle_media(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMIN_IDS:
        return

    caption = update.message.caption
    if not caption:
        await update.message.reply_text(
            "❌ يرجى كتابة اسم المادة والنوع في الـ Caption للشرح/الصورة/الملف.\n"
            "مثال للـ PDF: Human Anatomy I theoretical\n"
            "مثال للصورة: Human Anatomy I practical"
        )
        return

    file_id = None
    file_type = None

    if update.message.document:
        file_id = update.message.document.file_id
        file_type = "document"
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_type = "photo"

    if not file_id:
        return

    key = clean_text(caption).lower()

    db = load_data()
    if key not in db:
        db[key] = []
    
    db[key].append({"file_id": file_id, "type": file_type})
    save_data(db)

    await update.message.reply_text(f"✅ تم حفظ الوسيط بنجاح تحت الخانة:\n`{key}`", parse_mode="Markdown")

async def delete_material(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id not in ADMIN_IDS:
        return

    if not context.args:
        await update.message.reply_text("❌ يرجى كتابة اسم الخانة بعد الأمر.\nمثال:\n`/delete Human Anatomy I practical`", parse_mode="Markdown")
        return

    key = clean_text(" ".join(context.args)).lower()
    db = load_data()

    if key in db:
        del db[key]
        save_data(db)
        await update.message.reply_text(f"🗑️ تم حذف المحتويات الخاصة بـ: `{key}` بنجاح!", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ لم يتم العثور على محتويات بهذا الاسم.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    raw_text = update.message.text
    text = clean_text(raw_text)

    if 'stack' not in context.user_data:
        context.user_data['stack'] = []

    stack = context.user_data['stack']

    if raw_text == "🔙 Back":
        if stack:
            stack.pop()
        if not stack:
            reply_markup = ReplyKeyboardMarkup(MAIN_MENU, resize_keyboard=True)
            await update.message.reply_text("Main Menu - Select Level:", reply_markup=reply_markup)
        else:
            previous_state = stack[-1]
            await render_state(update, context, previous_state)
        return

    levels = {
        "Level 1": (LEVEL_1_MENU, "L1"),
        "Level 2": (LEVEL_2_MENU, "L2"),
        "Level 3": (LEVEL_3_MENU, "L3"),
        "Level 4": (LEVEL_4_MENU, "L4"),
        "Level 5": (LEVEL_5_MENU, "L5")
    }

    if text in levels:
        menu, state_code = levels[text]
        stack.append(state_code)
        await update.message.reply_text(f"{text} - Select Term/Semester:", reply_markup=ReplyKeyboardMarkup(menu, resize_keyboard=True))
        return

    if text in SUBJECTS:
        stack.append(f"TERM:{text}")
        buttons = [[KeyboardButton(subj)] for subj in SUBJECTS[text]]
        buttons.append([KeyboardButton("🔙 Back")])
        await update.message.reply_text(f"Subjects for {text}:", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))
        return

    if text in TYPES:
        stack.append(f"SUBJ:{text}")
        types_available = TYPES[text]
        buttons = [[KeyboardButton(t)] for t in types_available]
        buttons.append([KeyboardButton("🔙 Back")])
        await update.message.reply_text(f"Select section for {text}:", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))
        return

    if text in ["Theoretical", "Practical"]:
        current_subj = ""
        for item in reversed(stack):
            if item.startswith("SUBJ:"):
                current_subj = item.replace("SUBJ:", "")
                break

        search_key = f"{current_subj} {text}".strip().lower()
        db = load_data()

        if search_key in db and db[search_key]:
            for item in db[search_key]:
                if isinstance(item, dict):
                    if item.get("type") == "photo":
                        await update.message.reply_photo(photo=item["file_id"])
                    else:
                        await update.message.reply_document(document=item["file_id"])
                else:
                    await update.message.reply_document(document=item)
        else:
            await update.message.reply_text(f"No materials uploaded yet for {current_subj} ({text}).")
        return

async def render_state(update: Update, context: ContextTypes.DEFAULT_TYPE, state: str):
    if state == "L1":
        await update.message.reply_text("Level 1 - Select Semester:", reply_markup=ReplyKeyboardMarkup(LEVEL_1_MENU, resize_keyboard=True))
    elif state == "L2":
        await update.message.reply_text("Level 2 - Select Semester:", reply_markup=ReplyKeyboardMarkup(LEVEL_2_MENU, resize_keyboard=True))
    elif state == "L3":
        await update.message.reply_text("Level 3 - Select Semester:", reply_markup=ReplyKeyboardMarkup(LEVEL_3_MENU, resize_keyboard=True))
    elif state == "L4":
        await update.message.reply_text("Level 4 - Select Semester:", reply_markup=ReplyKeyboardMarkup(LEVEL_4_MENU, resize_keyboard=True))
    elif state == "L5":
        await update.message.reply_text("Level 5 - Select Term:", reply_markup=ReplyKeyboardMarkup(LEVEL_5_MENU, resize_keyboard=True))
    elif state.startswith("TERM:"):
        term_name = state.replace("TERM:", "")
        buttons = [[KeyboardButton(subj)] for subj in SUBJECTS[term_name]]
        buttons.append([KeyboardButton("🔙 Back")])
        await update.message.reply_text(f"Subjects for {term_name}:", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))
    elif state.startswith("SUBJ:"):
        subj_name = state.replace("SUBJ:", "")
        types_available = TYPES[subj_name]
        buttons = [[KeyboardButton(t)] for t in types_available]
        buttons.append([KeyboardButton("🔙 Back")])
        await update.message.reply_text(f"Select section for {subj_name}:", reply_markup=ReplyKeyboardMarkup(buttons, resize_keyboard=True))

def run_bot():
    while True:
        try:
            app = (
                Application.builder()
                .token(TOKEN)
                .connect_timeout(60.0)
                .read_timeout(60.0)
                .write_timeout(60.0)
                .get_updates_http_version("1.1")
                .http_version("1.1")
                .build()
            )
            
            app.add_handler(CommandHandler("start", start))
            app.add_handler(CommandHandler("delete", delete_material))
            app.add_handler(MessageHandler(filters.PHOTO | filters.ATTACHMENT, handle_media))
            app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
            
            print("Bot starting polling...")
            app.run_polling(drop_pending_updates=True)
        except Exception as e:
            print(f"Connection lost ({e}), restarting in 5 seconds...")
            time.sleep(5)

if __name__ == '__main__':
    run_bot()
