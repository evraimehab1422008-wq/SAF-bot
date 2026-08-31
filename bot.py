import os
import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# مسار مجلد البيانات للحفظ الدائم على Railway
DATA_DIR = "/app/data" if os.path.exists("/app/data") else "."
DATA_FILE = os.path.join(DATA_DIR, "bot_data.json")

# الهيكل الأساسي للبوت
# يمكنك إضافة "photo" أو "document" أو "sub_menu" لأي زر!
DEFAULT_MENU = {
    "Level 1": {
        "type": "sub_menu",
        "photo": "https://i.imgur.com/example_level1.jpg", # صورة توضيحية لـ Level 1 (اختياري)
        "caption": "مرحباً بك في المستوى الأول، اختر المادة:",
        "buttons": {
            "Anatomy": {
                "type": "sub_menu",
                "buttons": {
                    "Lecture 1 (PDF)": {
                        "type": "document",
                        "file_id": "BQACAgQAAxkBAAE...", # file_id الخاص بملف الـ PDF
                        "caption": "ملف المحاضرة الأولى أناتومي"
                    },
                    "Anatomy Diagram (Image)": {
                        "type": "photo",
                        "photo": "https://i.imgur.com/example_anatomy.jpg", # أو file_id للصورة
                        "caption": "رسم توضيحي للتشريح"
                    }
                }
            },
            "Physiology": {
                "type": "sub_menu",
                "buttons": {}
            }
        }
    },
    "Level 2": {
        "type": "sub_menu",
        "buttons": {}
    }
}

# تحميل وحفظ البيانات
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading data: {e}")
    return DEFAULT_MENU

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")

bot_structure = load_data()

# المساعدة في الحصول على القائمة الحالية بناءً على المسار
def get_current_node(path):
    curr = bot_structure
    for step in path:
        if isinstance(curr, dict) and "buttons" in curr:
            curr = curr["buttons"].get(step, {})
        elif isinstance(curr, dict):
            curr = curr.get(step, {})
    return curr

# دالة إظهار القائمة
async def show_node(update: Update, context: ContextTypes.DEFAULT_TYPE, path):
    node = get_current_node(path)
    
    # تحضير لوحة الأزرار
    keyboard = []
    if isinstance(node, dict) and "buttons" in node:
        button_names = list(node["buttons"].keys())
        # ترتيب الأزرار صفين صفين
        for i in range(0, len(button_names), 2):
            keyboard.append([KeyboardButton(b) for b in button_names[i:i+2]])
            
    if path:
        keyboard.append([KeyboardButton("🔙 Back"), KeyboardButton("🏠 Main Menu")])
    else:
        keyboard.append([KeyboardButton("🏠 Main Menu")])
        
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    caption = node.get("caption", "اختر من القائمة:") if isinstance(node, dict) else "اختر من القائمة:"
    photo = node.get("photo") if isinstance(node, dict) else None
    
    # إذا كان الزر يحتوي على صورة مع القائمة
    if photo:
        await update.message.reply_photo(photo=photo, caption=caption, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text=caption, reply_markup=reply_markup)

# أمر /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data['path'] = []
    await show_node(update, context, [])

# معالج الرسائل والأزرار
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    path = context.user_data.get('path', [])
    
    if text == "🏠 Main Menu":
        context.user_data['path'] = []
        await show_node(update, context, [])
        return
        
    if text == "🔙 Back":
        if path:
            path.pop()
            context.user_data['path'] = path
        await show_node(update, context, path)
        return

    current_node = get_current_node(path)
    buttons = current_node.get("buttons", {}) if isinstance(current_node, dict) else {}
    
    if text in buttons:
        selected = buttons[text]
        node_type = selected.get("type", "sub_menu")
        
        # 1. إذا كان العنصر عبارة عن صورة (Photo)
        if node_type == "photo":
            photo = selected.get("photo")
            caption = selected.get("caption", text)
            await update.message.reply_photo(photo=photo, caption=caption)
            
        # 2. إذا كان العنصر عبارة عن ملف/مستند (Document/PDF)
        elif node_type == "document":
            doc = selected.get("file_id")
            caption = selected.get("caption", text)
            await update.message.reply_document(document=doc, caption=caption)
            
        # 3. إذا كان العنصر قائمة فرعية (Sub-menu)
        elif node_type == "sub_menu":
            path.append(text)
            context.user_data['path'] = path
            await show_node(update, context, path)

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("Bot is running...")
    app.run_polling()
