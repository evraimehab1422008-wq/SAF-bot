import os
import json
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, 
    ContextTypes, filters
)

# مسار حفظ البيانات الدائم على Railway
DATA_DIR = "/app/data" if os.path.exists("/app/data") else "."
DATA_FILE = os.path.join(DATA_DIR, "bot_data.json")

# ضع أيدي تلجرام الخاص بك هنا لتتمكن من رفع الصور (يمكن معرفته من @userinfobot)
ADMIN_ID = 123456789  

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {
        "start": {"photo_id": None, "caption": "مرحباً بك! اختر المستوى:"},
        "children": {
            "Level 1": {
                "photo_id": None,
                "children": {
                    "Anatomy": {
                        "photo_id": None,
                        "children": {
                            "Practical": {"photo_id": None, "children": {}},
                            "Theoretical": {"photo_id": None, "children": {}}
                        }
                    }
                }
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

# البحث عن عقدة/زر بالاسم داخل الهيكل الشجري
def find_and_update_node(tree, target_name, photo_id):
    if target_name.lower() == "start":
        tree["start"]["photo_id"] = photo_id
        return True

    # البحث داخل الأبناء
    children = tree.get("children", {})
    if target_name in children:
        children[target_name]["photo_id"] = photo_id
        return True

    for key, node in children.items():
        if isinstance(node, dict) and "children" in node:
            if find_and_update_node(node, target_name, photo_id):
                return True
    return False

def get_node_by_path(path):
    curr = bot_data
    for step in path:
        curr = curr.get("children", {}).get(step, {})
    return curr

async def show_current_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    path = context.user_data.get('path', [])
    
    # إذا كنا في البداية (/start)
    if not path:
        node = bot_data.get("start", {})
        children = bot_data.get("children", {})
    else:
        node = get_node_by_path(path)
        children = node.get("children", {})

    # إعداد لوحة الأزرار
    keyboard = []
    keys = list(children.keys())
    for i in range(0, len(keys), 2):
        keyboard.append([KeyboardButton(k) for k in keys[i:i+2]])

    if path:
        keyboard.append([KeyboardButton("🔙 رجوع"), KeyboardButton("🏠 القائمة الرئيسية")])

    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

    caption = node.get("caption") or (path[-1] if path else "اختر من القائمة:")
    photo_id = node.get("photo_id")

    # إرسال الصورة إذا كانت مضافة لهذا القسم تحديداً
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

    # التحقق مما إذا كان النص المضغوط يطابق زراً متوفراً
    current_node = get_node_by_path(path) if path else bot_data
    children = current_node.get("children", {})

    if text in children:
        path.append(text)
        context.user_data['path'] = path
        await show_current_menu(update, context)

# دالة استقبال الصور وتخصيصها لأي زر أو أمر
async def handle_photo_upload(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id != ADMIN_ID:
        return

    caption = (update.message.caption or "").strip()
    if not caption:
        await update.message.reply_text("❌ يرجى كتابة اسم الزر أو القسم (مثلاً: start أو Level 1 أو Anatomy) في وصف الصورة (Caption).")
        return

    photo_id = update.message.photo[-1].file_id

    # تحديث الصورة للزر المطلوب
    success = find_and_update_node(bot_data, caption, photo_id)

    if success:
        save_data(bot_data)
        await update.message.reply_text(f"✅ تم ربط الصورة بنجاح بالقسم/الزر: `{caption}`")
    else:
        await update.message.reply_text(f"⚠️ لم يتم العثور على زر باسم `{caption}`. تأكد من كتابة الاسم بالظبط كما هو ظاهر في الأزرار.")

if __name__ == '__main__':
    TOKEN = os.getenv("BOT_TOKEN")
    app = ApplicationBuilder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_upload))

    print("Bot is running...")
    app.run_polling()
