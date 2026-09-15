import os
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🔑 التوكن والأدمن
BOT_TOKEN = os.getenv("BOT_TOKEN", "8791458947:AAGuTzvtNti_90CLWOs3nwB35i2pmdgVFmk")
ADMIN_IDS = [6448008082, 8791458947]

def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# 📚 هيكلة المواد والتراكات مع تقسيم (نظري / عملي) والإيموجيات
STRUCTURE = {
    "🎓 Level 1": {
        "Semester 1": {
            "🦴 Anatomy I": {"has_lab": True},
            "🫀 Physiology I": {"has_lab": True},
            "🧪 Biochemistry I": {"has_lab": True},
            "🔬 Histology": {"has_lab": True},
            "📐 Physics & Biomechanics": {"has_lab": False}
        },
        "Semester 2": {
            "🦴 Anatomy II": {"has_lab": True},
            "🫀 Physiology II": {"has_lab": True},
            "🧪 Biochemistry II": {"has_lab": True},
            "🏃 Kinesiology I": {"has_lab": True},
            "💊 Pharmacology": {"has_lab": False}
        }
    },
    "🎓 Level 2": {
        "Semester 3": {
            "🧠 Neuroanatomy": {"has_lab": True},
            "⚡ Electrotherapy I": {"has_lab": True},
            "🏋️ Hydrotherapy & Exercise": {"has_lab": True},
            "🏃 Kinesiology II": {"has_lab": True},
            "🩺 Pathology": {"has_lab": False}
        },
        "Semester 4": {
            "⚡ Electrotherapy II": {"has_lab": True},
            "👐 Manual Therapy": {"has_lab": True},
            "🩺 General Medicine & Surgery": {"has_lab": False},
            "🩻 Radiology & Imaging": {"has_lab": False}
        }
    },
    "🎓 Level 3 (Semester 1)": {
        "🦴 Musculoskeletal Physical Therapy": {"has_lab": True},
        "🧠 Neurological Physical Therapy": {"has_lab": True},
        "🩼 Biomechanics & Orthotics": {"has_lab": True},
        "🩺 Clinical Practice I": {"has_lab": True}
    },
    "🛣️ Tracks": {
        "🦴 Orthopedics Track": {
            "🦴 Orthopedic Assessment": {"has_lab": True},
            "💥 Traumatology & Sports Injuries": {"has_lab": True}
        },
        "🧠 Neurology Track": {
            "🧠 Neuro Rehab": {"has_lab": True},
            "🩺 Neurosurgery PT": {"has_lab": True}
        },
        "👶 Pediatrics Track": {
            "👶 Pediatric Rehab": {"has_lab": True},
            "🧸 Developmental Disorders": {"has_lab": True}
        },
        "🫀 Cardiopulmonary Track": {
            "🫀 ICU & Cardiac Rehab": {"has_lab": True},
            "🫁 Chest PT": {"has_lab": True}
        },
        "👵 Geriatrics & Women's Health Track": {
            "👵 Geriatric Rehab": {"has_lab": True},
            "🤰 Women's Health PT": {"has_lab": True}
        }
    }
}

# 💾 قاعدة بيانات الملفات المرفوعة
# Format: {"path_string": [{"name": ..., "file_id": ..., "type": ...}]}
file_database = {}

# 🚀 /start Command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["path"] = []
    context.user_data["deleting_mode"] = False
    await send_menu(update, context, "أهلاً بك في بوت مواد علاج طبيعي 🩺\nاختر القسم المطلوب من الكيبورد بالأسفل:")

# 📱 دالة بناء الكيبورد التفاعلي بدقة
async def send_menu(update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
    path = context.user_data.get("path", [])
    
    # الوصول للنود الحالية في الهيكل
    current_node = STRUCTURE
    for p in path:
        if isinstance(current_node, dict) and p in current_node:
            current_node = current_node[p]

    keyboard = []

    # 1. إذا كنا في مجلد أو قائمة مواد
    if isinstance(current_node, dict):
        keys = list(current_node.keys())
        # ترتيب الأزرار صفين صفين
        for i in range(0, len(keys), 2):
            row = [KeyboardButton(keys[i])]
            if i + 1 < len(keys):
                row.append(KeyboardButton(keys[i+1]))
            keyboard.append(row)

    # 2. إذا كنا وصلنا لمادة محددة تحتوي على (has_lab)
    elif isinstance(current_node, dict) == False:
        pass  # تدار في حالة أزرار النظرية/العملي

    # إضافة أزرار التحكم للأدمن والرجوع
    control_row = []
    if path:
        control_row.append(KeyboardButton("🔙 رجوع"))
        control_row.append(KeyboardButton("🏠 الرئيسية"))

    # خيارات الأدمن وقت ما يكون داخل مادة/قسم نظري أو عملي
    is_in_file_section = len(path) > 0 and (path[-1] in ["📖 Theoretical", "🔬 Practical"])
    if is_admin(update.effective_user.id) and is_in_file_section:
        control_row.append(KeyboardButton("🗑️ حذف ملف"))

    if control_row:
        keyboard.append(control_row)

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    # عرض الملفات إن وجدت في المسار الحالي
    path_key = " -> ".join(path)
    files = file_database.get(path_key, [])
    
    msg_text = text
    if is_in_file_section:
        msg_text += f"\n\n📍 **المسار:** {path_key}"
        if files:
            msg_text += "\n\n📚 **الملفات المتاحة:**\n"
            for idx, f in enumerate(files, 1):
                icon = "📄" if f["type"] == "document" else ("🖼️" if f["type"] == "photo" else "🎙️")
                msg_text += f"{idx}. {icon} {f['name']}\n"
        else:
            msg_text += "\n\n📂 لا توجد ملفات مرفوعة هنا حتى الآن."

        if is_admin(update.effective_user.id):
            msg_text += "\n\n⚙️ **[وضع الأدمن]:** يمكنك إرسال (PDF / صورة / ريكورد) مباشرة لرفعه هنا!"

    await update.message.reply_text(msg_text, reply_markup=reply_markup, parse_mode="Markdown")

# ⌨️ معالج الضغوطات على كيبورد الشاشة
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    path = context.user_data.get("path", [])
    user_id = update.effective_user.id

    # 1. زر الرئيسية
    if text == "🏠 الرئيسية":
        context.user_data["path"] = []
        context.user_data["deleting_mode"] = False
        await send_menu(update, context, "🏠 القائمة الرئيسية:")
        return

    # 2. زر الرجوع
    if text == "🔙 رجوع":
        if path:
            path.pop()
            # لو رجعنا من نظري/عملي نرجع خطوة كمان للمادة
            context.user_data["path"] = path
        context.user_data["deleting_mode"] = False
        await send_menu(update, context, "🔙 التراجع للخلف:")
        return

    # 3. وضع الحذف للأدمن
    if text == "🗑️ حذف ملف":
        if not is_admin(user_id):
            return
        path_key = " -> ".join(path)
        files = file_database.get(path_key, [])
        if not files:
            await update.message.reply_text("⚠️ لا توجد ملفات لحذفها في هذا القسم!")
            return
        
        context.user_data["deleting_mode"] = True
        delete_keyboard = [[KeyboardButton(f"❌ حذف: {f['name']}")] for f in files]
        delete_keyboard.append([KeyboardButton("🔙 رجوع")])
        await update.message.reply_text("اختر الملف الذي تريد حذفه:", reply_markup=ReplyKeyboardMarkup(delete_keyboard, resize_keyboard=True))
        return

    # تنفيذ الحذف
    if text.startswith("❌ حذف: ") and context.user_data.get("deleting_mode"):
        file_to_delete = text.replace("❌ حذف: ", "")
        path_key = " -> ".join(path)
        file_database[path_key] = [f for f in file_database[path_key] if f["name"] != file_to_delete]
        context.user_data["deleting_mode"] = False
        await update.message.reply_text(f"🗑️ تم حذف الملف: `{file_to_delete}` بنجاح!", parse_mode="Markdown")
        await send_menu(update, context, "تم التحديث:")
        return

    # الوصول لموقع المستخدم في الهيكل
    current_node = STRUCTURE
    for p in path:
        if isinstance(current_node, dict) and p in current_node:
            current_node = current_node[p]

    # اختيار قسم أو مادة
    if isinstance(current_node, dict) and text in current_node:
        item = current_node[text]
        path.append(text)
        context.user_data["path"] = path

        # لو المادة فيها lab نخيره بين نظري وعملي
        if isinstance(item, dict) and "has_lab" in item:
            keyboard = [[KeyboardButton("📖 Theoretical")]]
            if item["has_lab"]:
                keyboard[0].append(KeyboardButton("🔬 Practical"))
            keyboard.append([KeyboardButton("🔙 رجوع"), KeyboardButton("🏠 الرئيسية")])
            await update.message.reply_text(f"اختر القسم للمادة ({text}):", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))
            return
        else:
            await send_menu(update, context, f"📁 اخترت: {text}")
            return

    # اختيار نظري أو عملي للمادة
    if text in ["📖 Theoretical", "🔬 Practical"]:
        path.append(text)
        context.user_data["path"] = path
        await send_menu(update, context, f"📂 دخلت قسم: {text}")
        return

    # إرسال الملف المطلوب للمستخدم إذا ضغط على اسمه أو رقمه (عند تصفح الملفات)
    path_key = " -> ".join(path)
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

# 📤 رفع الملفات/الصور/الريكوردات من الأدمن مباشرة في المكان الحالي
async def handle_media_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if not is_admin(user_id):
        return

    path = context.user_data.get("path", [])
    if not path or path[-1] not in ["📖 Theoretical", "🔬 Practical"]:
        await update.message.reply_text("⚠️ يجب أن تدخل أولاً داخل قسم (Theoretical أو Practical) لمادة معينة حتى تتمكن من الرفع فيها!")
        return

    path_key = " -> ".join(path)
    if path_key not in file_database:
        file_database[path_key] = []

    if update.message.document:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name or "ملف PDF"
        file_type = "document"
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_name = update.message.caption or f"صورة_{len(file_database[path_key])+1}"
        file_type = "photo"
    elif update.message.voice or update.message.audio:
        media = update.message.voice or update.message.audio
        file_id = media.file_id
        file_name = update.message.caption or f"تسجيل_صوتي_{len(file_database[path_key])+1}"
        file_type = "audio"
    else:
        return

    file_database[path_key].append({
        "name": file_name,
        "file_id": file_id,
        "type": file_type
    })

    await update.message.reply_text(f"✅ تم رفع `{file_name}` بنجاح في هذا القسم!", parse_mode="Markdown")
    await send_menu(update, context, "تحديث القسم:")

# 🏁 تشغيل السكربت
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    
    # فلتر رفع الوسائط للأدمن
    media_filter = filters.Document.ALL | filters.PHOTO | filters.VOICE | filters.AUDIO
    app.add_handler(MessageHandler(media_filter, handle_media_upload))
    
    # معالج الرسائل النصية والضغط على كيبورد الشاشة
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 البوت يعمل بالهيكلية الكيبوردية الجديدة...")
    app.run_polling()
        
