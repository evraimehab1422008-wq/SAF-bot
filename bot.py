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

TOKEN = "8791458947:AAFCsqj64LQ5q2MrjvG0u5kMA6AXbT5pKFI"

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

# Core Physical Therapy Subjects Only
CURRICULUM = {
    "Level 1 🥇": {
        "Semester 1 📚": {
            "ANAT_111": {"name": "Human Anatomy I 🦴", "lab": True},
            "BIOC_111": {"name": "Biochemistry I 🧪", "lab": False},
            "HIST_111": {"name": "Histology 🔬", "lab": True},
            "HPHY_111": {"name": "Human Physiology I 🫀", "lab": True},
        },
        "Semester 2 📚": {
            "ANAT_112": {"name": "Human Anatomy II 🦴", "lab": True},
            "BIOC_112": {"name": "Biochemistry II 🧪", "lab": False},
            "HPHY_112": {"name": "Human Physiology II 🫀", "lab": True},
            "BIOM_112": {"name": "Kinesiology I 🦵", "lab": True},
            "BIOP_112": {"name": "Biophysics II ⚡", "lab": True},
        }
    },
    "Level 2 🥈": {
        "Semester 3 📚": {
            "ANAT_211": {"name": "Neuroanatomy 🧠", "lab": True},
            "BIOM_211": {"name": "Biomechanics II ⚙️", "lab": True},
            "BS_221": {"name": "Electrotherapy I ⚡", "lab": True},
            "BS_211": {"name": "Evaluation & Measurements I 📏", "lab": True},
            "HPHY_211": {"name": "Neurophysiology 🧠", "lab": False},
            "BS_231": {"name": "Therapeutic Exercises I 🏋️‍♂️", "lab": True},
        },
        "Semester 4 📚": {
            "BIOM_212": {"name": "Biomechanics III ⚙️", "lab": True},
            "CMED_211": {"name": "Community Health & Hygiene 🏥", "lab": False},
            "BS_212": {"name": "Evaluation & Measurements II 📏", "lab": True},
            "HPHY_212": {"name": "Exercise Physiology 🏃‍♂️", "lab": False},
            "PATH_212": {"name": "Pathology for PT 🔬", "lab": False},
            "BS_232": {"name": "Manual Therapy 👐", "lab": True},
            "BS_222": {"name": "Electrotherapy II ⚡", "lab": True},
            "ANAT_212": {"name": "Human Anatomy IV 🦴", "lab": True},
            "BS_255": {"name": "Legal & Ethical Issues ⚖️", "lab": False},
        }
    },
    "Level 3 🥉": {
        "Semester 5 📚": {
            "BIOM_311": {"name": "Biomechanics IV ⚙️", "lab": True},
            "BS_341": {"name": "Hydrotherapy 🌊", "lab": True},
            "BS_355": {"name": "Research & Medical Statistics 📊", "lab": False},
            "BS_357": {"name": "Management & Clinical Decision 📋", "lab": False},
            "PAPH_311": {"name": "Pathophysiology 🩺", "lab": False},
            "PHAR_311": {"name": "Pharmacology for PT 💊", "lab": False},
            "REHA_311": {"name": "Rehabilitation ♿", "lab": False},
        },
        "Semester 6 - Batna Term 🫁": {
            "MED_312": {"name": "Medicine for Cardiovascular 🫀", "lab": False},
            "MED_314": {"name": "Medicine for Pulmonary & Internal 🫁", "lab": False},
            "CAPU_312": {"name": "Clinical Practice for Geriatrics 👴", "lab": True},
            "CAPU_314": {"name": "Clinical Practice for Cardio & Pulm 🩺", "lab": True},
            "CAPU_326": {"name": "Geriatric Rehabilitation 👵", "lab": True},
            "CAPU_324": {"name": "PT for Pulmonary & Internal 🫁", "lab": True},
            "CAPU_322": {"name": "PT for Cardiovascular Disorders 🫀", "lab": True},
            "BIOC_312": {"name": "Clinical Nutrition 🥗", "lab": False},
            "PSYC_312": {"name": "Psychology for Handicapped 🧠", "lab": False},
            "RAD_312": {"name": "Radiology 🩻", "lab": False},
        }
    },
    "Level 4 🏅": {
        "Semester 7 - Gyna Term 🤰": {
            "BIOM_411": {"name": "Ergonomics 🪑", "lab": True},
            "SURG_411": {"name": "Clinical Practice Integumentary 🩺", "lab": True},
            "PT_421": {"name": "PT for Integumentary & Surgical 🩹", "lab": True},
            "SURG_GYPD": {"name": "Clinical Practice for Women Health 🚺", "lab": True},
            "GYPD_421": {"name": "PT for Women Health 🤰", "lab": True},
            "MED_411": {"name": "Clinical Medicine for Women Health 🏥", "lab": False},
            "PT_441": {"name": "Evidence Based Practice 📑", "lab": False},
            "SURG_411_GEN": {"name": "General Surgery & ICU 😷", "lab": False},
        },
        "Semester 8 - Orthopedic Term 🦴": {
            "MED_412": {"name": "Medicine for Traumatology 🚑", "lab": False},
            "SURG_412": {"name": "Medicine for Orthopedic Surgery 🦴", "lab": False},
            "MUSK_422": {"name": "Physical Diagnosis & Exam 🔍", "lab": True},
            "MUSK_424": {"name": "PT for Orthopedics 🦵", "lab": True},
            "PROS_412": {"name": "Orthotics & Prosthetics 🦾", "lab": True},
            "RAD_412": {"name": "Radiodiagnosis 🩻", "lab": False},
            "MUSK_426": {"name": "Sport Physical Therapy ⚽", "lab": True},
            "MUSK_412": {"name": "Clinical Practice Orthopedics 🏥", "lab": True},
        }
    },
    "Level 5 🏆": {
        "Semester 9 - Pediatric Term 👶": {
            "MED_511": {"name": "Clinical Medicine for Pediatrics 👶", "lab": False},
            "GYPD_511": {"name": "Clinical Practice Pediatrics 🧸", "lab": True},
            "GYPD_521": {"name": "Motor Development Across Life Span 👶➡️👴", "lab": True},
            "GYPD_525": {"name": "PT for Pediatrics 👶", "lab": True},
            "GYPD_527": {"name": "PT for Pediatric Surgical 🏥", "lab": True},
            "GYPD_529": {"name": "Speech Therapy 🗣️", "lab": False},
            "OT_511": {"name": "Occupational Therapy 🎨", "lab": False},
        },
        "Semester 10 - Neuro Term 🧠": {
            "MED_512": {"name": "Clinical Medicine for Neurology 🧠", "lab": False},
            "NEUR_512": {"name": "Clinical Practice Neurosurgery 🏥", "lab": True},
            "NEUR_522": {"name": "PT for Neurological Conditions 🧠", "lab": True},
            "NEUR_524": {"name": "PT for Neurosurgical Conditions 🔪", "lab": True},
            "SURG_512": {"name": "Neurosurgery 🧠", "lab": False},
            "NEUR_526": {"name": "Recent Approaches in Neuro Rehab 🧬", "lab": True},
            "NEUR_525": {"name": "Electrodiagnosis ⚡", "lab": True},
            "PT_541": {"name": "Motor Learning & Control 🦾", "lab": False},
        }
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    keyboard = [[KeyboardButton(level)] for level in CURRICULUM.keys()]
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text("🎓 Welcome to Physical Therapy Hub!\nSelect Academic Level:", reply_markup=reply_markup)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "🏠 Main Menu":
        await start(update, context)
        return

    # Level selection
    if text in CURRICULUM:
        context.user_data['level'] = text
        context.user_data['current_path'] = None
        keyboard = [[KeyboardButton(sem)] for sem in CURRICULUM[text].keys()]
        keyboard.append([KeyboardButton("🏠 Main Menu")])
        await update.message.reply_text(f"Selected: {text}\nSelect Semester:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    # Semester selection
    level = context.user_data.get('level')
    if level and text in CURRICULUM[level]:
        context.user_data['semester'] = text
        context.user_data['current_path'] = None
        subjects = CURRICULUM[level][text]
        keyboard = [[KeyboardButton(subj_info["name"])] for subj_code, subj_info in subjects.items()]
        keyboard.append([KeyboardButton("🏠 Main Menu")])
        await update.message.reply_text(f"Selected: {text}\nSelect Subject:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    # Subject selection
    semester = context.user_data.get('semester')
    if level and semester:
        subjects = CURRICULUM[level][semester]
        for subj_code, subj_info in subjects.items():
            if text == subj_info["name"]:
                context.user_data['subject_code'] = subj_code
                context.user_data['subject_name'] = text
                context.user_data['current_path'] = None
                
                keyboard = [[KeyboardButton("Theoretical 📖")]]
                if subj_info["lab"]:
                    keyboard.append([KeyboardButton("Practical 🔬")])
                keyboard.append([KeyboardButton("🏠 Main Menu")])
                
                await update.message.reply_text(f"Selected Subject: {text}\nSelect Type:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
                return

    # Section selection (Theoretical / Practical)
    if text in ["Theoretical 📖", "Practical 🔬"]:
        subj_code = context.user_data.get('subject_code')
        subj_name = context.user_data.get('subject_name')
        if not subj_code:
            await update.message.reply_text("⚠️ Please select a subject first.")
            return

        sec_type = "THEORY" if "Theoretical" in text else "PRACTICAL"
        section_path = f"{subj_code}_{sec_type}"
        context.user_data['current_path'] = section_path

        items = db_get_files(section_path)
        
        keyboard = [
            [KeyboardButton("🗑 Delete Content")],
            [KeyboardButton("🏠 Main Menu")]
        ]
        
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
        
        msg = f"📍 *{subj_name}* ({text})\n\n"
        if items:
            msg += f"📦 Available Files/Images: {len(items)}\n"
            msg += "👇 *Send any PDF or Image right now to store it here!*"
        else:
            msg += "📂 No content uploaded yet.\n"
            msg += "👇 *Send any PDF or Image right now to store it here!*"

        await update.message.reply_text(msg, parse_mode="Markdown", reply_markup=reply_markup)

        for idx, item in enumerate(items):
            if item["type"] == "document":
                await update.message.reply_document(document=item["file_id"], caption=f"File #{idx+1}")
            elif item["type"] == "photo":
                await update.message.reply_photo(photo=item["file_id"], caption=f"Image #{idx+1}")
        return

    # Delete Menu Action
    if text == "🗑 Delete Content":
        current_path = context.user_data.get('current_path')
        if not current_path:
            await update.message.reply_text("⚠️ No active section selected.")
            return
            
        items = db_get_files(current_path)
        if not items:
            await update.message.reply_text("📂 No items available to delete in this section.")
            return
            
        keyboard = []
        for idx, item in enumerate(items):
            icon = "📄 PDF" if item["type"] == "document" else "🖼 Photo"
            keyboard.append([KeyboardButton(f"❌ Delete Item #{item['db_id']} ({icon})")])
        keyboard.append([KeyboardButton("🏠 Main Menu")])
        
        await update.message.reply_text("Select an item to delete:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        return

    # Item Deletion Trigger
    if text.startswith("❌ Delete Item #"):
        try:
            db_id = int(text.split("#")[1].split()[0])
            db_delete_file(db_id)
            await update.message.reply_text("✅ Item deleted successfully!")
            
            current_path = context.user_data.get('current_path')
            if current_path:
                items = db_get_files(current_path)
                keyboard = [[KeyboardButton("🗑 Delete Content")], [KeyboardButton("🏠 Main Menu")]]
                await update.message.reply_text(f"Remaining items in section: {len(items)}", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
        except Exception:
            await update.message.reply_text("⚠️ Error processing deletion.")
        return

async def handle_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    current_path = context.user_data.get('current_path')
    
    if not current_path:
        await update.message.reply_text("⚠️ Please navigate to a specific section (Theoretical 📖 or Practical 🔬) before sending files!")
        return

    if update.message.document:
        file_id = update.message.document.file_id
        file_type = "document"
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_type = "photo"
    else:
        return

    db_add_file(current_path, file_id, file_type)
    await update.message.reply_text("✅ File successfully saved to this section!")

if __name__ == '__main__':
    print("🤖 Starting Bot...")
    application = ApplicationBuilder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_upload))

    print("✅ Bot is online!")
    application.run_polling(drop_pending_updates=True)
