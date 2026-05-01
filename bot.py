import os
import sqlite3
import logging
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton, BotCommand
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# 1. إعداد السجلات
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# 2. إعداد قاعدة البيانات
def init_db():
    conn = sqlite3.connect('mkbotx.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS users
                      (user_id INTEGER PRIMARY KEY, username TEXT, balance REAL DEFAULT 0.0)''')
    cursor.execute('''CREATE TABLE IF NOT EXISTS buttons
                      (keyword TEXT PRIMARY KEY, response TEXT)''')
    conn.commit()
    conn.close()

init_db()

# 3. ميزة الوصف الاحترافي (التي طلبتها)
async def update_bot_description(context: ContextTypes.DEFAULT_TYPE):
    full_description = (
        "🎯 MKBotX_Bot (v0.0.1)\n\n"
        "Helps you create your own bots with menus. From Games to Online Stores.\n\n"
        "(🌐) LANG: EN, AR, RU (+10 more).(文)\n\n"
        "👾(☰) IN MENU ⠿\n"
        "Create menu, Mailing, Feedback forms, Inline menu, Macros, Commands, "
        "Referral system, Balance and Variables, Bonus, Exchange, Auto Payments and MORE\n\n"
        "🏰 IN GROUP\n"
        "Subscription check, Moderator, Triggers, Feedback forms\n\n"
        "🛒 IN SHOP 💸\n"
        "Categories, Shopping Cart, Client Profile, Order management, Payments\n\n"
        "🎩 IN AD MARKET 🎭\n"
        "Send Ads to over 7 Million people. Receive Ads to earn"
    )
    try:
        await context.bot.set_my_description(full_description)
        await context.bot.set_my_short_description("Create professional bots with menus and stores 🚀")
        logging.info("✅ تم تحديث الوصف بنجاح")
    except Exception as e:
        logging.error(f"❌ خطأ في الوصف: {e}")

# 4. الواجهة الرئيسية
def get_main_keyboard():
    keyboard = [
        [KeyboardButton("🎩 طلب الإعلان"), KeyboardButton("🛠️ إدارة البوتات")],
        [KeyboardButton("أعد تعبئة مع تيليجرام «⭐ نجوم»")],
        [KeyboardButton("📞 جهات الاتصال"), KeyboardButton("❓ مساعدة")]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# 5. معالجات الأوامر
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دالة الترحيب: تقوم بحفظ المستخدم وإرسال 3 رسائل ترحيبية منفصلة"""
    user = update.effective_user
    
    # 1. حفظ المستخدم في قاعدة البيانات (فتح اتصال وإغلاقه لضمان الأمان)
    conn = sqlite3.connect('mkbotx.db')
    cursor = conn.cursor()
    # استخدام INSERT OR IGNORE لمنع تكرار البيانات أو حذف القديم
    cursor.execute("INSERT OR IGNORE INTO users (user_id, username) VALUES (?, ?)", 
                   (user.id, user.username))
    conn.commit()
    conn.close()

    # --- الرسالة الأولى: الترحيب واللغات ---
    first_message = (
        f"👋 Hello {user.first_name}!\n"
        "Menu Builder Bot will help you to create your own bot with menu.\n\n"
        "You can change your language:\n"
        "🇬🇧English . . . . . . /langen\n"
        "🇷🇺Русский . . . . . . /langru\n\n"
        "Collaborative translations:\n"
        "🇵🇸Arabic     [ 88%] . /langar\n"
        "🇪🇸Español    [ 73%] . /langes\n"
        "🇫🇷Francais   [ 92%] . /langfr\n"
        "🇹🇷Türkçe     [ 86%] . /langtr\n\n"
        "Needs to be translated: Amharic, Deutsch, Hindi."
    )
    await update.message.reply_text(first_message)

    # --- الرسالة الثانية: القائمة الرئيسية (مع الكيبورد السفلي) ---
    second_message = "🔝 Main menu\n\nPress «🛠 Manage Bots» to start!"
    # استدعاء دالة get_main_keyboard لظهور الأزرار السفلية
    await update.message.reply_text(second_message, reply_markup=get_main_keyboard())

    # --- الرسالة الثالثة: التنبيه بالاشتراك الإجباري (مع زر شفاف) ---
    third_message = (
        "❗️ATTENTION\n"
        "You see this message because you are not subscribed to the channel:\n"
        "@MenuBuilderNews\n\n"
        "It is important that you are up to date with the latest updates.\n"
        "ℹ️ This message will disappear upon subscription (within 1 day)."
    )
    
    # إنشاء زر شفاف للانضمام للقناة
    keyboard = [[InlineKeyboardButton("📢 Join Channel", url="https://t.me/MenuBuilderNews")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(third_message, reply_markup=reply_markup)

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    if text == "🛠️ إدارة البوتات":
        await update.message.reply_text("🚧 قسم إدارة البوتات قيد التطوير...")
    elif text == "🎩 طلب الإعلان":
        await update.message.reply_text("📢 تواصل مع الإدارة لطلب إعلان.")
    elif text == "❓ مساعدة":
        await update.message.reply_text("💡 الدعم الفني متوفر 24/7.")
    else:
        await update.message.reply_text("استخدم القائمة بالأسفل.")
# --- 6. التشغيل النهائي البسيط ---
if __name__ == '__main__':
    # التوكن الخاص بك من BotFather
    TOKEN = "ضع-التوكن—الخاص–بك-هنا"

    # بناء التطبيق بأبسط صورة ممكنة
    application = Application.builder().token(TOKEN).build()

    # ربط الأوامر والرسائل
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))

    # تشغيل مهمة تحديث الوصف بعد 10 ثواني من التشغيل
    if application.job_queue:
        application.job_queue.run_once(update_bot_description, 10)

    print("🚀 جاري تشغيل MKBotX... اذهب للتأكد من التيليجرام الآن!")

    # تشغيل مباشر بدون إعدادات معقدة
    application.run_polling()
