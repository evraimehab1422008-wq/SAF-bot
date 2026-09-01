import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# 1. التوكين الجديد كلياً
TOKEN = "8791458947:AAHj6eWae2zCAVY3zZmBOOToyel8b3LMnY0"

# ضبط التسجيل (Logging) لمعرفة الأخطاء إن وجدت
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """قائمة البداية الرئيسية"""
    keyboard = [
        [
            InlineKeyboardButton("📊 الخطة الرمضانية", callback_data="btn_plan"),
            InlineKeyboardButton("📜 الجدول التفاعلي", callback_data="btn_schedule"),
        ],
        [
            InlineKeyboardButton("🤲 أدعية رمضانية", callback_data="btn_duaa"),
            InlineKeyboardButton("💡 نصائح وإرشادات", callback_data="btn_tips"),
        ],
        [
            InlineKeyboardButton("🔔 التنبيهات والأذكار", callback_data="btn_reminders"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    welcome_text = (
        "🌙 **أهلاً بك في بوت رفيق رمضان المبارك!** 🌙\n\n"
        "نسأل الله أن يبلغنا وإياكم شهر رمضان ويوفقنا فيه لصالح الأعمال.\n"
        "اختر من القائمة أدناه للبدء:"
    )
    
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
    elif update.callback_query:
        query = update.callback_query
        await query.answer()
        await query.edit_message_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """التحكم بالأزرار واستجاباتها"""
    query = update.callback_query
    await query.answer()
    
    back_button = [[InlineKeyboardButton("🔙 العودة للقائمة الرئيسية", callback_data="btn_main")]]
    reply_markup = InlineKeyboardMarkup(back_button)

    if query.data == "btn_main":
        await start(update, context)
        
    elif query.data == "btn_plan":
        text = (
            "📊 **الخطة الرمضانية اليومية:**\n\n"
            "1️⃣ **القرآن الكريم:** ختمة واحدة على الأقل (جزء يومياً بعد كل صلاة 4 صفحات).\n"
            "2️⃣ **الصلوات:** المحافظة على الفروض في أوقاتها + السنن الراتبة + صلاة التراويح.\n"
            "3️⃣ **الصدقة:** تخصيص مبلغ بسيط يومياً أو الإطعام.\n"
            "4️⃣ **الذكر:** مائة مرة استغفار + تسبيح + تحميد."
        )
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")
        
    elif query.data == "btn_schedule":
        text = (
            "📜 **الجدول التفاعلي المقترح:**\n\n"
            "🔹 **الفجر:** قراءة أذكار الصباح + قراءة جزء من القرآن.\n"
            "🔹 **الظهر:** صلاة النافلة والاستغفار.\n"
            "🔹 **العصر:** قراءة أذكار المساء والدعاء.\n"
            "🔹 **المغرب:** الإفطار والدعاء المستجاب عند الإفطار.\n"
            "🔹 **العشاء:** صلاة التراويح والقيام."
        )
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == "btn_duaa":
        text = (
            "🤲 **أدعية رمضانية مباركة:**\n\n"
            "✨ *دعاء الإفطار:* «ذهب الظمأ وابتلت العروق وثبت الأجر إن شاء الله».\n\n"
            "✨ *دعاء ليلة القدر:* «اللهم إنك عفو كريم تحب العفو فاعفُ عني».\n\n"
            "✨ *دعاء جامع:* «رَبَّنَا آتِنَا فِي الدُّنْيَا حَسَنَةً وَفِي الآخِرَةِ حَسَنَةً وَقِنَا عَذَابَ النَّارِ»."
        )
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == "btn_tips":
        text = (
            "💡 **نصائح لتنظيم الوقت والاستفادة من الشهر:**\n\n"
            "• قلل من استخدام وسائل التواصل الاجتماعي ومشتتات الانتباه.\n"
            "• حافظ على نمط نوم متوازن وتناول غذاء صحي أثناء السحور والإفطار.\n"
            "• احرص على الدعاء قبل الإفطار مباشرة فله مزية عظيمة."
        )
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

    elif query.data == "btn_reminders":
        text = (
            "🔔 **التنبيهات والأذكار:**\n\n"
            "سيتم إرسال الأذكار والتنبيهات اليومية لك تلقائياً خلال شهر رمضان المبارك لتذكيرك بالطاعات!"
        )
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode="Markdown")

def main():
    app = ApplicationBuilder().token(TOKEN).build()
    
    # المعالجات (Handlers)
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    
    print("البوت يعمل الآن بنجاح...")
    app.run_polling()

if __name__ == '__main__':
    main()
