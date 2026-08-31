import os
import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    ContextTypes, filters
)

# -------------------------------------------------------------
# الإعدادات والتوكين الجديد
# -------------------------------------------------------------
BOT_TOKEN_DEFAULT = "8791458947:AAGkFPigOOvCJNcpfoKGOG54wBPdc-thtJY"
ADMIN_ID = 1422008432
# -------------------------------------------------------------

# هيكل الأزرار المباشر بالإيموجيات لضمان عدم اختفائها إطلاقاً
bot_data = {
    "photo_id": None,
    "caption": "🎓 مرحباً بك! اختر المستوى الدراسي:",
    "buttons": {
        "📚 Level 1": {
            "photo_id": None,
            "caption": "📖 مرحباً بك في Level 1، اختر المادة:",
            "buttons": {
                "🦴 Anatomy": {
                    "photo_id": None,
                    "caption": "🦴 قسم التشريح Anatomy",
                    "buttons": {}
                },
                "⚡ Physiology": {
                    "photo_id": None,
                    "caption": "⚡ قسم الفيزيولوجي Physiology",
                    "buttons": {}
                },
                "🔬 Histology": {
                    "photo_id": None,
                    "caption": "🔬 قسم الأنسجة Histology",
                    "buttons": {}
                }
            }
        },
        "📘 Level 2": {
            "photo_id": None,
            "caption": "📖 مرحباً بك في Level 2، اختر المادة:",
            "buttons": {
                "🧪 Biochemistry": {
                    "photo_id": None,
                    "caption": "🧪 قسم الكيمياء الحيوية Biochemistry",
                    "buttons": {}
                },
                "💊 Pharmacology": {
                    "photo_id": None,
                    "caption": "💊 قسم الأدوية Pharmacology",
                    "buttons": {}
                }
            }
        }
    }
}

def get_node_by_path(path):
    curr = bot_data
    for step in path:
        if isinstance(curr, dict) and "buttons" in curr and step in curr["buttons"]:
            curr = curr["buttons"][step]
        else:
            return None
    return curr

async def show_current_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = context.user_data.get('path', [])
    node = get_node_by_path(path)
    
    if node is None:
        path = []
        context.user_data['path'] = []
        node = bot_data

    buttons = node.get("buttons", {})
    keyboard = []
    keys = list(buttons.keys())
    
    # تنظيم الأزرار صفين صفين
    for i in range(0, len(keys), 2):
        keyboard.append([KeyboardButton(k) for k in keys[i:i+2]])

    if path:
        keyboard.append([KeyboardButton("🔙 رجوع"), KeyboardButton("🏠 القائمة الرئيسية")])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) if keyboard else None

    caption = node.get("caption") or (path[-1] if path else "اختر من القائمة:")
    photo_id = node.get("photo_id")

    if photo_id:
        try:
            await update.message.reply_photo(photo=photo_id, caption=caption, reply_markup=reply_markup)
        except Exception:
            await update.message.reply_text(text=caption, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=caption, reply_markup=reply_markup)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['path'] = []
    await show_current_menu(update, context)

async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    path = context.user_data.get('path', [])

    if text == "🏠 القائمة الرئيسية":
        context.user_data['path'] = []
        await show_current_menu(update, context)
        return

    if text == "🔙 رجوع":
        if path:
            path.pop()
            context.user_data['path'] = path
        await show_current_menu(update, context)
        return

    node = get_node_by_path(path)
    buttons = node.get("buttons", {}) if node else {}

    if text in buttons:
        path.append(text)
        context.user_data['path'] = path
        await show_current_menu(update, context)

async def add_button_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    new_btn_name = " ".join(context.args).strip()
    if not new_btn_name:
        await update.message.reply_text("❌ اكتب اسم الزر بعد الأمر، مثال:\n`/add 📁 Level 3`", parse_mode="Markdown")
        return

    path = context.user_data.get('path', [])
    node = get_node_by_path(path)

    if node is not None:
        if "buttons" not in node:
            node["buttons"] = {}
        node["buttons"][new_btn_name] = {"photo_id": None, "caption": f"قسم {new_btn_name}", "buttons": {}}
        await update.message.reply_text(f"✅ تم إضافة الزر `{new_btn_name}` بنجاح!", parse_mode="Markdown")
        await show_current_menu(update, context)

async def handle_photo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        return

    path = context.user_data.get('path', [])
    node = get_node_by_path(path)

    if node is not None:
        photo_id = update.message.photo[-1].file_id
        node["photo_id"] = photo_id
        
        current_location = path[-1] if path else "صفحة البداية (Start)"
        await update.message.reply_text(f"📸 تم حفظ الصورة بنجاح وربطها بـ: `{current_location}`", parse_mode="Markdown")
        await show_current_menu(update, context)

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN") or BOT_TOKEN_DEFAULT
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("add", add_button_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_upload))

    print("Bot is running...")
    app.run_polling()
