import logging
import sqlite3
from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8791458947:AAFa5UpBX81-I_jV9lLzuEI4cD073dQ5qyg"

# 🔑 ضَع أرقام الـ User IDs الخاصة بالأدمنز هنا
ADMIN_IDS = [6448008082،8791458947]

# Database Setup
def init_db():
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS files (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_path TEXT NOT NULL,
            file_id TEXT NOT NULL,
            file_type TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

init_db()

def db_add_file(section_path, file_id, file_type):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('INSERT INTO files (section_path, file_id, file_type) VALUES (?, ?, ?)',
                   (section_path, file_id, file_type))
    conn.commit()
    conn.close()

def db_get_files(section_path):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('SELECT id, file_id, file_type FROM files WHERE section_path = ?', (section_path,))
    rows = cursor.fetchall()
    conn.close()
    return [{"db_id": row[0], "file_id": row[1], "type": row[2]} for row in rows]

def db_delete_file(db_id):
    conn = sqlite3.connect('bot_data.db')
    cursor = conn.cursor()
    cursor.execute('DELETE FROM files WHERE id = ?', (db_id,))
    conn.commit()
    conn.close()

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# Structure Definition
CURRICULUM = {
    "Level 1 🥇": {
        "ANAT_111": {"name": "Human Anatomy I 🦴", "lab": True, "tracks": ["Main 📌"]},
        "BIOC_111": {"name": "Biochemistry I 🧪", "lab": False, "tracks": ["Main 📌"]},
        "HIST_111": {"name": "Histology 🔬", "lab": True, "tracks": ["Main 📌"]},
        "HPHY_111": {"name": "Human Physiology I 🫀", "lab": True, "tracks": ["Main 📌"]},
        "ANAT_112": {"name": "Human Anatomy II 🦴", "lab": True, "tracks": ["Main 📌"]},
        "BIOC_112": {"name": "Biochemistry II 🧪", "lab": False, "tracks": ["Main 📌"]},
        "HPHY_112": {"name": "Human Physiology II 🫀", "lab": True, "tracks": ["Main 📌"]},
        "BIOM_112": {"name": "Kinesiology I 🦵", "lab": True, "tracks": ["Main 📌"]},
        "BIOP_112": {"name": "Biophysics II ⚡", "lab": True, "tracks": ["Main 📌"]},
    },
    "Level 2 🥈": {
        "ANAT_211": {"name": "Neuroanatomy 🧠", "lab": True, "tracks": ["Main 📌"]},
        "BIOM_211": {"name": "Biomechanics II ⚙️", "lab": True, "tracks": ["Main 📌"]},
        "BS_221": {"name": "Electrotherapy I ⚡", "lab": True, "tracks": ["Main 📌"]},
        "BS_211": {"name": "Evaluation & Measurements I 📏", "lab": True, "tracks": ["Main 📌"]},
        "HPHY_211": {"name": "Neurophysiology 🧠", "lab": False, "tracks": ["Main 📌"]},
        "BS_231": {"name": "Therapeutic Exercises I 🏋️‍♂️", "lab": True, "tracks": ["Main 📌"]},
        "BIOM_212": {"name": "Biomechanics III ⚙️", "lab": True, "tracks": ["Main 📌"]},
        "CMED_211": {"name": "Community Health & Hygiene 🏥", "lab": False, "tracks": ["Main 📌"]},
        "BS_212": {"name": "Evaluation & Measurements II 📏", "lab": True, "tracks": ["Main 📌"]},
        "HPHY_212": {"name": "Exercise Physiology 🏃‍♂️", "lab": False, "tracks": ["Main 📌"]},
        "PATH_212": {"name": "Pathology for PT 🔬", "lab": False, "tracks": ["Main 📌"]},
        "BS_232": {"name": "Manual Therapy 👐", "lab": True, "tracks": ["Main 📌"]},
        "BS_222": {"name": "Electrotherapy II ⚡", "lab": True, "tracks": ["Main 📌"]},
        "ANAT_212": {"name": "Human Anatomy IV 🦴", "lab": True, "tracks": ["Main 📌"]},
        "BS_255": {"name": "Legal & Ethical Issues ⚖️", "lab": False, "tracks": ["Main 📌"]},
    },
    "Level 3 🥉": {
        "Semester 5 📚": {
            "BIOM_311": {"name": "Biomechanics IV ⚙️", "lab": True, "tracks": ["Main 📌"]},
            "BS_341": {"name": "Hydrotherapy 🌊", "lab": True, "tracks": ["Main 📌"]},
            "BS_355": {"name": "Research & Medical Statistics 📊", "lab": False, "tracks": ["Main 📌"]},
            "BS_357": {"name": "Management & Clinical Decision 📋", "lab": False, "tracks": ["Main 📌"]},
            "PAPH_311": {"name": "Pathophysiology 🩺", "lab": False, "tracks": ["Main 📌"]},
            "PHAR_311": {"name": "Pharmacology for PT 💊", "lab": False, "tracks": ["Main 📌"]},
            "REHA_311": {"name": "Rehabilitation ♿", "lab": False, "tracks": ["Main 📌"]},
        },
        "Term Batna 🫁": {
            "BATNA_MAIN": {"name": "General Subjects 📚", "lab": True, "tracks": ["General Track 🟢"]},
            "RAD_312": {"name": "Radiology 🩻", "lab": False, "tracks": ["Radiology Track 🟡"]},
            "CARDIO_312": {"name": "Cardio & Pulmonary 🫀", "lab": True, "tracks": ["Cardio Track 🔴"]},
        }
    },
    "Level 4 🏅": {
        "Term Gyna 🤰": {
            "GYNA_MAIN": {"name": "General & Surgery 🏥", "lab": True, "tracks": ["General & Surgery 🩺"]},
            "GYNA_PT": {"name": "Gynaecology & Women Health 🤰", "lab": True, "tracks": ["Gyna Track 🌸"]},
        },
        "Term Ortho 🦴": {
            "ORTHO_MED": {"name": "Orthopedic Surgery & Traumatology 🦴", "lab": False, "tracks": ["Medical Ortho 🩺"]},
            "ORTHO_PT": {"name": "Physical Therapy for Orthopedics 🦵", "lab": True, "tracks": ["PT Ortho 🏋️‍♂️"]},
        }
    },
    "Level 5 🏆": {
        "Term Pedia 👶": {
            "PEDIA_MED": {"name": "Pediatric Medicine & Surgery 👶", "lab": False, "tracks": ["Pediatric Medicine 🏥"]},
            "PEDIA_PT": {"name": "Physical Therapy for Pediatrics 🧸", "lab": True, "tracks": ["Pediatric PT 🎨"]},
        },
        "Term Neuro 🧠": {
            "NEURO_MED": {"name": "Neurology & Neurosurgery 🧠", "lab": False, "tracks": ["Neurology Medicine 🏥"]},
            "NEURO_PT": {"name": "Physical Therapy for Neurology 🦾", "lab": True, "tracks": ["Neurology PT 🧬"]},
        }
    }
}

async def display_section(update: Update, context: ContextTypes.DEFAULT_TYPE, path_title: str, path_id: str, keyboard_options: list):
    user_id = update.effective_user.id
    user_is_admin = is_admin(user_id)
    
    context.user_data['current_path'] = path_id
    items = db_get_files(path_id)
    
    nav_buttons = []
    if path_id != "ROOT":
        nav_buttons.append(KeyboardButton("🔙 Back"))
        nav_buttons.append(KeyboardButton("🏠 Main Menu"))
    
    final_keyboard = keyboard_options + ([nav_buttons] if nav_buttons else [])
    
    if items and path_id != "ROOT" and user_is_admin:
        final_keyboard.insert(0, [KeyboardButton("🗑 Delete Content")])
        
    reply_markup = ReplyKeyboardMarkup(final_keyboard, resize_keyboard=True)
    
    msg = f"📍 *{path_title}*\n\n"
    if items:
        msg += f"📦 Available Files/Images: {len(items)}\n"
    else:
        msg += "📂 No extra content uploaded here yet.\n"
    
    if user_is_admin:
        msg += "👇 *[Admin Mode]* You can send any PDF or Image right now to save it in this section!"

    await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

    for idx, item in enumerate(items):
        file_caption = f"File #{idx+1} [ID: {item['db_id']}]" if user_is_admin else None
        if item["type"] == "document":
            await update.message.reply_document(document=item["file_id"], caption=file_caption)
        elif item["type"] == "photo":
            await update.message.reply_photo(photo=item["file_id"], caption=file_caption)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    context.user_data['step_history'] = []
    keyboard = [[KeyboardButton(level)] for level in CURRICULUM.keys()]
    await display_section(update, context, "Main Menu - Academic Levels", "ROOT", keyboard)

async def handle_back(update: Update, context: ContextTypes.DEFAULT_TYPE):
    history = context.user_data.get('step_history', [])
    if not history:
        await start(update, context)
        return
    
    prev_step = history.pop()
    context.user_data['step_history'] = history
    
    step_type = prev_step.get('type')
    if step_type == 'ROOT':
        await start(update, context)
    elif step_type == 'LEVEL':
        level = prev_step['level']
        context.user_data['level'] = level
        data = CURRICULUM[level]
        if "ANAT_111" in data or "ANAT_211" in data:
            keyboard = [[KeyboardButton(subj_info["name"])] for subj_code, subj_info in data.items()]
        else:
            keyboard = [[KeyboardButton(sem)] for sem in data.keys()]
        await display_section(update, context, f"Level: {level}", f"LEVEL_{level}", keyboard)
    elif step_type == 'SEMESTER':
        level = prev_step['level']
        sem = prev_step['semester']
        context.user_data['level'] = level
        context.user_data['semester'] = sem
        subjects = CURRICULUM[level][sem]
        keyboard = [[KeyboardButton(subj_info["name"])] for subj_code, subj_info in subjects.items()]
        await display_section(update, context, f"{level} > {sem}", f"SEM_{sem}", keyboard)
    elif step_type == 'SUBJECT':
        level = prev_step['level']
        sem = prev_step.get('semester')
        subj_code = prev_step['subj_code']
        subj_name = prev_step['subj_name']
        context.user_data['level'] = level
        context.user_data['semester'] = sem
        context.user_data['subject_code'] = subj_code
        context.user_data['subject_name'] = subj_name
        
        subj_info = CURRICULUM[level][sem][subj_code] if sem else CURRICULUM[level][subj_code]
        keyboard = [[KeyboardButton("Theoretical 📖")]]
        if subj_info["lab"]:
            keyboard.append([KeyboardButton("Practical 🔬")])
        await display_section(update, context, f"Subject: {subj_name}", f"SUBJ_{subj_code}", keyboard)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_id = update.effective_user.id
    history = context.user_data.get('step_history', [])

    if text == "🏠 Main Menu":
        await start(update, context)
        return

    if text == "🔙 Back":
        await handle_back(update, context)
        return

    # 1. Level Selection
    if text in CURRICULUM:
        history.append({'type': 'ROOT'})
        context.user_data['step_history'] = history
        context.user_data['level'] = text
        data = CURRICULUM[text]
        
        # إذا كان Level 1 أو Level 2 يعرض المواد المباشرة
        if text in ["Level 1 🥇", "Level 2 🥈"]:
            keyboard = [[KeyboardButton(subj_info["name"])] for subj_code, subj_info in data.items()]
        else:
            keyboard = [[KeyboardButton(sem)] for sem in data.keys()]
            
        await display_section(update, context, f"Level: {text}", f"LEVEL_{text}", keyboard)
        return

    # 2. Semester/Term Selection
    level = context.user_data.get('level')
    if level and level in CURRICULUM and isinstance(CURRICULUM[level], dict):
        if text in CURRICULUM[level] and isinstance(CURRICULUM[level][text], dict):
            history.append({'type': 'LEVEL', 'level': level})
            context.user_data['step_history'] = history
            context.user_data['semester'] = text
            subjects = CURRICULUM[level][text]
            keyboard = [[KeyboardButton(subj_info["name"])] for subj_code, subj_info in subjects.items()]
            await display_section(update, context, f"{level} > {text}", f"SEM_{text}", keyboard)
            return

    # 3. Subject Selection
    semester = context.user_data.get('semester')
    subjects_to_check = {}
    if level and level in CURRICULUM:
        if semester and semester in CURRICULUM[level]:
            subjects_to_check = CURRICULUM[level][semester]
        elif level in ["Level 1 🥇", "Level 2 🥈"]:
            subjects_to_check = CURRICULUM[level]

    for subj_code, subj_info in subjects_to_check.items():
        if text == subj_info["name"]:
            if semester:
                history.append({'type': 'SEMESTER', 'level': level, 'semester': semester})
            else:
                history.append({'type': 'LEVEL', 'level': level})
                
            context.user_data['step_history'] = history
            context.user_data['subject_code'] = subj_code
            context.user_data['subject_name'] = text
            
            keyboard = [[KeyboardButton("Theoretical 📖")]]
            if subj_info["lab"]:
                keyboard.append([KeyboardButton("Practical 🔬")])
            await display_section(update, context, f"Subject: {text}", f"SUBJ_{subj_code}", keyboard)
            return

    # 4. Section Selection (Theoretical / Practical)
    if text in ["Theoretical 📖", "Practical 🔬"]:
        subj_code = context.user_data.get('subject_code')
        subj_name = context.user_data.get('subject_name')
        if not subj_code:
            await update.message.reply_text("⚠️ Please select a subject first.")
            return

        history.append({'type': 'SUBJECT', 'level': level, 'semester': semester, 'subj_code': subj_code, 'subj_name': subj_name})
        context.user_data['step_history'] = history

        sec_type = "THEORY" if "Theoretical" in text else "PRACTICAL"
        section_path = f"{subj_code}_{sec_type}"
        await display_section(update, context, f"{subj_name} ({text})", section_path, [])
        return

    # 5. Delete Menu Action (Admin Only)
    if text == "🗑 Delete Content":
        if not is_admin(user_id):
            await update.message.reply_text("🚫 Only admins can delete content.")
            return
            
        current_path = context.user_data.get('current_path', 'ROOT')
        items = db_get_files(current_path)
        if not items:
            await update.message.reply_text("📂 No items available to delete in this section.")
            return
            
        keyboard = []
        for idx, item in enumerate(items):
            icon = "📄 PDF" if item["type"] == "document" else "🖼 Photo"
            keyboard.append([KeyboardButton(f"❌ Delete Item #{item['db_id']} ({icon})")])
        keyboard.append([KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main Menu")])
        
        await update.message.reply_text("Select an item to delete:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    # 6. Item Deletion Trigger (Admin Only)
    if text.startswith("❌ Delete Item #"):
        if not is_admin(user_id):
            await update.message.reply_text("🚫 Only admins can delete content.")
            return
            
        try:
            db_id = int(text.split("#")[1].split()[0])
            db_delete_file(db_id)
            await update.message.reply_text("✅ Item deleted successfully!")
            current_path = context.user_data.get('current_path', 'ROOT')
            items = db_get_files(current_path)
            keyboard = [[KeyboardButton("🗑 Delete Content")]] if items else []
            keyboard.append([KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main Menu")])
            await update.message.reply_text(f"Remaining items here: {len(items)}", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        except Exception:
            await update.message.reply_text("⚠️ Error processing deletion.")
        return

async def handle_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        await update.message.reply_text("🚫 Only admins can upload photos or files to the bot.")
        return

    current_path = context.user_data.get('current_path', 'ROOT')

    if update.message.document:
        file_id = update.message.document.file_id
        file_type = "document"
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_type = "photo"
    else:
        return

    db_add_file(current_path, file_id, file_type)
    await update.message.reply_text("✅ Saved successfully to current section!")

if __name__ == '__main__':
    print("🤖 Starting Bot...")
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_upload))

    print("✅ Bot is online!")
    application.run_polling(drop_pending_updates=True)
