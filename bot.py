import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# 🔑 التوكن والأدمن المحددين من قبلك
BOT_TOKEN = "8791458947:AAHv374AGV8-c-QZL_gCFt8Y4ydKQBSTlm4"
ADMIN_IDS = [6448008082, 8791458947]

# 💾 قاعدة بيانات مؤقتة لتخزين الأقسام والملفات
data_store = {
    "Level 1": {
        "Semester 1": {"Anatomy": [], "Physiology": []},
        "Semester 2": {"Biochemistry": []}
    },
    "Level 2": {
        "Semester 3": {"Neuroanatomy": [], "Electrotherapy I": []}
    }
}

# 🛠️ دالة للتحقق من صفة الأدمن
def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_IDS

# 🚀 أمر البداية /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["path"] = []
    await show_current_level(update, context)

# 📱 عرض القائمة أو المادة الحالية
async def show_current_level(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = context.user_data.get("path", [])
    
    current_node = data_store
    for p in path:
        current_node = current_node[p]

    keyboard = []
    
    # 1. إذا كنا في مجلد فرعي
    if isinstance(current_node, dict):
        for key in current_node.keys():
            keyboard.append([InlineKeyboardButton(f"📁 {key}", callback_data=f"nav:{key}")])
    
    # 2. إذا كنا داخل مادة تحتوي على ملفات
    elif isinstance(current_node, list):
        if not current_node:
            text_content = "📂 هذا القسم فارغ حالياً."
        else:
            for idx, item in enumerate(current_node):
                icon = "📄" if item["type"] == "document" else ("🖼️" if item["type"] == "photo" else "🎙️")
                row = [InlineKeyboardButton(f"{icon} {item['name']}", callback_data=f"view:{idx}")]
                
                # إضافة زر الحذف للأدمن فقط
                if is_admin(update.effective_user.id):
                    row.append(InlineKeyboardButton("❌ حذف", callback_data=f"delete:{idx}"))
                
                keyboard.append(row)

    # زر الرجوع للخلف 🔙
    if path:
        keyboard.append([InlineKeyboardButton("🔙 رجوع", callback_data="nav_back")])

    markup = InlineKeyboardMarkup(keyboard)
    
    path_str = " ⬅️ ".join(path) if path else "القائمة الرئيسية 🏠"
    admin_notice = "\n\n⚙️ **[وضع الأدمن]:** أرسل (PDF/صورة/صوت) مباشرة لرفعه في هذا القسم!" if is_admin(update.effective_user.id) and isinstance(current_node, list) else ""
    
    msg_text = f"📍 **الموقع الحالي:** {path_str}{admin_notice}"

    if update.callback_query:
        await update.callback_query.edit_message_text(msg_text, reply_markup=markup, parse_mode="Markdown")
    else:
        await update.message.reply_text(msg_text, reply_markup=markup, parse_mode="Markdown")

# 🖱️ معالجة تفاعلات الأزرار
async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    data = query.data
    path = context.user_data.get("path", [])

    if data.startswith("nav:"):
        selected = data.split("nav:")[1]
        path.append(selected)
        context.user_data["path"] = path
        await show_current_level(update, context)

    elif data == "nav_back":
        if path:
            path.pop()
            context.user_data["path"] = path
        await show_current_level(update, context)

    elif data.startswith("view:"):
        idx = int(data.split("view:")[1])
        current_node = data_store
        for p in path:
            current_node = current_node[p]
        
        file_info = current_node[idx]
        file_id = file_info["file_id"]
        
        if file_info["type"] == "document":
            await query.message.reply_document(document=file_id, caption=f"📄 {file_info['name']}")
        elif file_info["type"] == "photo":
            await query.message.reply_photo(photo=file_id, caption=f"🖼️ {file_info['name']}")
        elif file_info["type"] == "audio":
            await query.message.reply_audio(audio=file_id, caption=f"🎙️ {file_info['name']}")

    elif data.startswith("delete:"):
        if not is_admin(query.from_user.id):
            await query.answer("🛑 هذه الصلاحية للأدمن فقط!", show_alert=True)
            return

        idx = int(data.split("delete:")[1])
        current_node = data_store
        for p in path:
            current_node = current_node[p]
        
        deleted_item = current_node.pop(idx)
        await query.answer(f"🗑️ تم حذف {deleted_item['name']} بنجاح!", show_alert=True)
        await show_current_level(update, context)

# 📤 معالجة الرفع المباشر للأدمن في المكان الحالي
async def handle_media_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    
    if not is_admin(user_id):
        return

    path = context.user_data.get("path", [])
    if not path:
        await update.message.reply_text("⚠️ يرجى الدخول إلى القسم المطلوب أولاً قبل إرسال الملفات!")
        return

    current_node = data_store
    for p in path:
        current_node = current_node[p]

    if not isinstance(current_node, list):
        await update.message.reply_text("⚠️ يرجى الدخول داخل المادة نفسها لرفع الملفات (وليس في القائمة الرئيسية).")
        return

    # تحديد نوع الملف المعالج
    if update.message.document:
        file_id = update.message.document.file_id
        file_name = update.message.document.file_name or "ملف PDF"
        file_type = "document"
    elif update.message.photo:
        file_id = update.message.photo[-1].file_id
        file_name = update.message.caption or "صورة"
        file_type = "photo"
    elif update.message.voice or update.message.audio:
        media = update.message.voice or update.message.audio
        file_id = media.file_id
        file_name = update.message.caption or "تسجيل صوتي"
        file_type = "audio"
    else:
        return

    current_node.append({
        "name": file_name,
        "file_id": file_id,
        "type": file_type
    })

    await update.message.reply_text(f"✅ تم الرفع بنجاح في هذا القسم: `{file_name}`", parse_mode="Markdown")
    await show_current_level(update, context)

# 🏁 تشغيل السكربت
if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_callback))
    
    media_filter = filters.Document.ALL | filters.PHOTO | filters.VOICE | filters.AUDIO
    app.add_handler(MessageHandler(media_filter, handle_media_upload))

    print("🤖 البوت يعمل الآن بنجاح مع بيانات التوكن والأدمن الخاصة بك...")
    app.run_polling()
