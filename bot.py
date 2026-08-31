import os
import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    ContextTypes, filters
)

# -------------------------------------------------------------
# الإعدادات الخاصة بك
# -------------------------------------------------------------
BOT_TOKEN = "7649581977:AAEUw7v4yK88m1-uVn6w7-O4M9n4y12345"
ADMIN_ID = 1422008432
# -------------------------------------------------------------

DATA_DIR = "/app/data" if os.path.exists("/app/data") else "."
DATA_FILE = os.path.join(DATA_DIR, "bot_data.json")

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "start": {"photo_id": None, "caption": "مرحباً بك! اختر المستوى:"},
        "structure": {
            "Level 1": {
                "photo_id": None,
                "children": {}
            },
            "Level 2": {
                "photo_id": None,
                "children": {}
            }
        }
    }

def save_data(data):
    try:
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving data: {e}")

bot_data = load_data()

# دالة للبحث والتعديل في الشجرة أو إنشائها إن لم تكن موجودة
def update_or_create_node(tree, target_name, photo_id):
    if target_name.lower() in ["start", "/start"]:
        if "start" not in tree:
            tree["start"] = {}
        tree["start"]["photo_id"] = photo_id
        return True

    struct = tree.get("structure", {})

    # 1. إذا كان الاسم موجوداً في المستوى الأول مباشر
    if target_name in struct:
        struct[target_name]["photo_id"] = photo_id
        return True

    # 2. البحث داخل الأبناء الموزعين
    def search_recursive(nodes):
        for key, node in nodes.items():
            if key == target_name:
                node["photo_id"] = photo_id
                return True
            if "children" in node and isinstance(node["children"], dict):
                if search_recursive(node["children"]):
                    return True
        return False

    if search_recursive(struct):
        return True

    # 3. إذا لم يكن موجوداً نهائياً، أضفه كزر جديد في الشجرة الرئيسية ليعمل فوراً
    struct[target_name] = {
        "photo_id": photo_id,
        "children": {}
    }
    return True

def get_node_by_path(path):
    curr = bot_data.get("structure", {})
    target_node = None
    for step in path:
        if step in curr:
            target_node = curr[step]
            curr = target_node.get("children", {})
        else:
            return None
    return target_node, curr

async def show_current_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = context.user_data.get('path', [])
    
    if not path:
        node = bot_data.get("start", {})
        children = bot_data.get("structure", {})
    else:
        node, children = get_node_by_path(path)
        if node is None:
            node = {}
            children = {}

    keyboard = []
    keys = list(children.keys()) if isinstance(children, dict) else []
    for i in range(0, len(keys), 2):
        keyboard.append([KeyboardButton(k) for k in keys[i:i+2]])

    if path:
        keyboard.append([KeyboardButton("🔙 رجوع"), KeyboardButton("🏠 القائمة الرئيسية")])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True) if keyboard else None

    caption = node.get("caption") or (path[-1] if path else "اختر من القائمة:")
    photo_id = node.get("photo_id")

    if photo_id:
        await update.message.reply_photo(photo=photo_id, caption=caption, reply_markup=reply_markup)
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

    if not path:
        children = bot_data.get("structure", {})
    else:
        _, children = get_node_by_path(path)

    if isinstance(children, dict) and text in children:
        path.append(text)
        context.user_data['path'] = path
        await show_current_menu(update, context)

async def handle_photo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        return

    caption = (update.message.caption or "").strip()
    if not caption:
        await update.message.reply_text("❌ يرجى كتابة اسم الزر أو القسم (مثلاً: start أو Level 1) في الـ Caption مع الصورة.")
        return

    photo_id = update.message.photo[-1].file_id

    update_or_create_node(bot_data, caption, photo_id)
    save_data(bot_data)
    await update.message.reply_text(f"✅ تم حفظ الصورة بنجاح وربطها بالقسم/الزر: `{caption}`")

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN", BOT_TOKEN)
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_upload))

    print("Bot is running...")
    app.run_polling()
