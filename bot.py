import logging
import sqlite3
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import (
    ApplicationBuilder,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

# Logging configuration
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

TOKEN = "8791458947:AAFCsqj64LQ5q2MrjvG0u5kMA6AXbT5pKFI"
ALLOWED_USER_ID = 6448008082

# Database Setup for permanent storage
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

# Curriculum Database
CURRICULUM = {
    "L1": {
        "title": "Level 1 🥇",
        "semesters": {
            "S1": {
                "title": "Semester 1 📚",
                "subjects": {
                    "ANAT_111": {"name": "Human Anatomy I 🦴", "lab": True},
                    "BIOC_111": {"name": "Biochemistry I 🧪", "lab": False},
                    "HIST_111": {"name": "Histology 🔬", "lab": True},
                    "HPHY_111": {"name": "Human Physiology I 🫀", "lab": True},
                    "COMP_101": {"name": "Intro to Computer 💻", "lab": False},
                    "ENGL_101": {"name": "English Language I 📖", "lab": False},
                    "HUMN_101": {"name": "Behavioral Psychology 🧠", "lab": False},
                }
            },
            "S2": {
                "title": "Semester 2 📚",
                "subjects": {
                    "ANAT_112": {"name": "Human Anatomy II 🦴", "lab": True},
                    "BIOC_112": {"name": "Biochemistry II 🧪", "lab": False},
                    "HPHY_112": {"name": "Human Physiology II 🫀", "lab": True},
                    "BIOM_112": {"name": "Kinesiology I 🦵", "lab": True},
                    "BIOP_112": {"name": "Biophysics II ⚡", "lab": True},
                    "SOCI_112": {"name": "Intro to Sociology 🌐", "lab": False},
                    "ENGL_102": {"name": "English Language II 📖", "lab": False},
                    "HUMN_102": {"name": "Scientific Thinking 💡", "lab": False},
                }
            }
        }
    },
    "L2": {
        "title": "Level 2 🥈",
        "semesters": {
            "S3": {
                "title": "Semester 3 📚",
                "subjects": {
                    "ANAT_211": {"name": "Neuroanatomy 🧠", "lab": True},
                    "BIOM_211": {"name": "Biomechanics II ⚙️", "lab": True},
                    "BS_221": {"name": "Electrotherapy I ⚡", "lab": True},
                    "BS_211": {"name": "Evaluation & Measurements I 📏", "lab": True},
                    "HPHY_211": {"name": "Neurophysiology 🧠", "lab": False},
                    "BS_231": {"name": "Therapeutic Exercises I 🏋️‍♂️", "lab": True},
                    "ENGL_201": {"name": "English Language III 📖", "lab": False},
                }
            },
            "S4": {
                "title": "Semester 4 📚",
                "subjects": {
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
            }
        }
    },
    "L3": {
        "title": "Level 3 🥉",
        "semesters": {
            "S5": {
                "title": "Semester 5 📚",
                "subjects": {
                    "BIOM_311": {"name": "Biomechanics IV ⚙️", "lab": True},
                    "BS_341": {"name": "Hydrotherapy 🌊", "lab": True},
                    "BS_355": {"name": "Research & Medical Statistics 📊", "lab": False},
                    "BS_357": {"name": "Management & Clinical Decision 📋", "lab": False},
                    "PAPH_311": {"name": "Pathophysiology 🩺", "lab": False},
                    "PHAR_311": {"name": "Pharmacology for PT 💊", "lab": False},
                    "REHA_311": {"name": "Rehabilitation ♿", "lab": False},
                    "ARAB_101": {"name": "Arabic Language ✍️", "lab": False},
                }
            },
            "S6": {
                "title": "Semester 6 - Batna Term 🫁",
                "subjects": {
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
            }
        }
    },
    "L4": {
        "title": "Level 4 🏅",
        "semesters": {
            "S7": {
                "title": "Semester 7 - Gyna Term 🤰",
                "subjects": {
                    "BIOM_411": {"name": "Ergonomics 🪑", "lab": True},
                    "SURG_411": {"name": "Clinical Practice Integumentary 🩺", "lab": True},
                    "PT_421": {"name": "PT for Integumentary & Surgical 🩹", "lab": True},
                    "SURG_GYPD": {"name": "Clinical Practice for Women Health 🚺", "lab": True},
                    "GYPD_421": {"name": "PT for Women Health 🤰", "lab": True},
                    "MED_411": {"name": "Clinical Medicine for Women Health 🏥", "lab": False},
                    "PT_441": {"name": "Evidence Based Practice 📑", "lab": False},
                    "SURG_411_GEN": {"name": "General Surgery & ICU 😷", "lab": False},
                }
            },
            "S8": {
                "title": "Semester 8 - Orthopedic Term 🦴",
                "subjects": {
                    "MED_412": {"name": "Medicine for Traumatology 🚑", "lab": False},
                    "SURG_412": {"name": "Medicine for Orthopedic Surgery 🦴", "lab": False},
                    "MUSK_422": {"name": "Physical Diagnosis & Exam 🔍", "lab": True},
                    "MUSK_424": {"name": "PT for Orthopedics 🦵", "lab": True},
                    "PROS_412": {"name": "Orthotics & Prosthetics 🦾", "lab": True},
                    "RAD_412": {"name": "Radiodiagnosis 🩻", "lab": False},
                    "MUSK_426": {"name": "Sport Physical Therapy ⚽", "lab": True},
                    "MUSK_412": {"name": "Clinical Practice Orthopedics 🏥", "lab": True},
                }
            }
        }
    },
    "L5": {
        "title": "Level 5 🏆",
        "semesters": {
            "S9": {
                "title": "Semester 9 - Pediatric Term 👶",
                "subjects": {
                    "MED_511": {"name": "Clinical Medicine for Pediatrics 👶", "lab": False},
                    "GYPD_511": {"name": "Clinical Practice Pediatrics 🧸", "lab": True},
                    "GYPD_521": {"name": "Motor Development Across Life Span 👶➡️👴", "lab": True},
                    "GYPD_525": {"name": "PT for Pediatrics 👶", "lab": True},
                    "GYPD_527": {"name": "PT for Pediatric Surgical 🏥", "lab": True},
                    "GYPD_529": {"name": "Speech Therapy 🗣️", "lab": False},
                    "OT_511": {"name": "Occupational Therapy 🎨", "lab": False},
                }
            },
            "S10": {
                "title": "Semester 10 - Neuro Term 🧠",
                "subjects": {
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
    }
}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ALLOWED_USER_ID:
        await update.message.reply_text("⛔ Access Denied: Unauthorized User.")
        return

    context.user_data['current_path'] = None
    keyboard = [[InlineKeyboardButton("Start 🚀", callback_data="show_levels")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = "Welcome to Physical Therapy Academic Hub! 🎓\n\nClick Start to explore levels and courses."
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(welcome_text, reply_markup=reply_markup)

async def show_levels(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    keyboard = []
    for level_key, level_data in CURRICULUM.items():
        keyboard.append([InlineKeyboardButton(level_data["title"], callback_data=f"lvl_{level_key}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text("Select Academic Level:", reply_markup=reply_markup)

async def show_semesters(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    level_key = query.data.split("_")[1]
    level_data = CURRICULUM[level_key]
    
    keyboard = []
    for sem_key, sem_data in level_data["semesters"].items():
        keyboard.append([InlineKeyboardButton(sem_data["title"], callback_data=f"sem_{level_key}_{sem_key}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Back to Levels", callback_data="show_levels")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"Selected: {level_data['title']}\nSelect Semester:", reply_markup=reply_markup)

async def show_subjects(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    level_key, sem_key = parts[1], parts[2]
    sem_data = CURRICULUM[level_key]["semesters"][sem_key]
    
    keyboard = []
    for subj_key, subj_data in sem_data["subjects"].items():
        keyboard.append([InlineKeyboardButton(subj_data["name"], callback_data=f"sbj_{level_key}_{sem_key}_{subj_key}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Back to Semesters", callback_data=f"lvl_{level_key}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"Selected: {sem_data['title']}\nSelect Subject:", reply_markup=reply_markup)

async def show_type_options(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    level_key, sem_key, subj_key = parts[1], parts[2], parts[3]
    subj_data = CURRICULUM[level_key]["semesters"][sem_key]["subjects"][subj_key]
    
    keyboard = []
    keyboard.append([InlineKeyboardButton("Theoretical 📖", callback_data=f"sec_{level_key}_{sem_key}_{subj_key}_THEORY")])
    
    if subj_data["lab"]:
        keyboard.append([InlineKeyboardButton("Practical 🔬", callback_data=f"sec_{level_key}_{sem_key}_{subj_key}_PRACTICAL")])
        
    keyboard.append([InlineKeyboardButton("⬅️ Back to Subjects", callback_data=f"sem_{level_key}_{sem_key}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(f"Subject: {subj_data['name']}\nSelect Section:", reply_markup=reply_markup)

async def view_section(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    level_key, sem_key, subj_key, sec_type = parts[1], parts[2], parts[3], parts[4]
    
    section_path = f"{level_key}_{sem_key}_{subj_key}_{sec_type}"
    context.user_data['current_path'] = section_path
    
    subj_name = CURRICULUM[level_key]["semesters"][sem_key]["subjects"][subj_key]["name"]
    sec_title = "Theoretical 📖" if sec_type == "THEORY" else "Practical 🔬"
    
    items = db_get_files(section_path)
    
    msg = f"📍 *{subj_name}* - *{sec_title}*\n\n"
    if items:
        msg += f"📦 Available Files/Images: {len(items)}\n"
        msg += "👇 Send any PDF/Image to add content to this section.\n"
    else:
        msg += "📂 No content uploaded yet.\n"
        msg += "👇 Send any PDF or Image to store it here!"

    keyboard = []
    if items:
        keyboard.append([InlineKeyboardButton("🗑 Delete Content", callback_data=f"delmenu_{section_path}")])
    keyboard.append([InlineKeyboardButton("⬅️ Back", callback_data=f"sbj_{level_key}_{sem_key}_{subj_key}")])
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    await query.edit_message_text(msg, parse_mode="Markdown", reply_markup=reply_markup)
    
    for idx, item in enumerate(items):
        if item["type"] == "document":
            await query.message.reply_document(document=item["file_id"], caption=f"File #{idx+1}")
        elif item["type"] == "photo":
            await query.message.reply_photo(photo=item["file_id"], caption=f"Image #{idx+1}")

async def handle_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ALLOWED_USER_ID:
        return

    current_path = context.user_data.get('current_path')
    if not current_path:
        await update.message.reply_text("⚠️ Please navigate to a specific section (Theoretical or Practical) first before sending files.")
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
    
    keyboard = [[InlineKeyboardButton("View Section Content 📂", callback_data=f"sec_{current_path}")]]
    await update.message.reply_text("✅ File successfully saved permanently!", reply_markup=InlineKeyboardMarkup(keyboard))

async def show_delete_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    section_path = query.data.replace("delmenu_", "")
    items = db_get_files(section_path)
    
    if not items:
        await query.edit_message_text("No files to delete!")
        return

    keyboard = []
    for idx, item in enumerate(items):
        icon = "📄 PDF" if item["type"] == "document" else "🖼 Photo"
        keyboard.append([InlineKeyboardButton(f"Delete Item #{idx+1} ({icon})", callback_data=f"rem_{item['db_id']}_{section_path}")])
    
    keyboard.append([InlineKeyboardButton("⬅️ Back to Section", callback_data=f"sec_{section_path}")])
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await query.edit_message_text("Select specific item to delete:", reply_markup=reply_markup)

async def execute_delete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    parts = query.data.split("_")
    db_id = int(parts[1])
    section_path = "_".join(parts[2:])
    
    db_delete_file(db_id)
    await query.answer("✅ Selected item deleted successfully!", show_alert=True)
    
    keyboard = [[InlineKeyboardButton("⬅️ Return to Section", callback_data=f"sec_{section_path}")]]
    await query.edit_message_text("Item has been deleted successfully.", reply_markup=InlineKeyboardMarkup(keyboard))

if __name__ == '__main__':
    print("🤖 Starting Bot...")
    application = ApplicationBuilder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(show_levels, pattern="^show_levels$"))
    application.add_handler(CallbackQueryHandler(show_semesters, pattern="^lvl_"))
    application.add_handler(CallbackQueryHandler(show_subjects, pattern="^sem_"))
    application.add_handler(CallbackQueryHandler(show_type_options, pattern="^sbj_"))
    application.add_handler(CallbackQueryHandler(view_section, pattern="^sec_"))
    application.add_handler(CallbackQueryHandler(show_delete_menu, pattern="^delmenu_"))
    application.add_handler(CallbackQueryHandler(execute_delete, pattern="^rem_"))
    
    application.add_handler(MessageHandler(filters.Document.ALL | filters.PHOTO, handle_upload))
    
    print("✅ Bot is online!")
    application.run_polling(drop_pending_updates=True)
