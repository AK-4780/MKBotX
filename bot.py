import os
import sqlite3
import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# 1. إعداد السجلات (Logging) لمراقبة الأخطاء في الترمينال
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

# --- إعدادات قاعدة البيانات ---
def init_db():
    conn = sqlite3.connect('bots.db')
    cursor = conn.cursor()
    cursor.execute('''CREATE TABLE IF NOT EXISTS buttons 
                      (name TEXT PRIMARY KEY, reply TEXT)''')
    conn.commit()
    conn.close()

def get_buttons():
    conn = sqlite3.connect('bots.db')
    cursor = conn.cursor()
    cursor.execute("SELECT name, reply FROM buttons")
    rows = cursor.fetchall()
    conn.close()
    return dict(rows)

def save_button(name, reply):
    conn = sqlite3.connect('bots.db')
    cursor = conn.cursor()
    cursor.execute("INSERT OR REPLACE INTO buttons (name, reply) VALUES (?, ?)", (name, reply))
    conn.commit()
    conn.close()

# --- وظائف البوت ---

# وظيفة تعيين وصف البوت (تظهر للمستخدمين الجدد)
async def set_bot_description(context: ContextTypes.DEFAULT_TYPE):
    description = """
🎯 MKBotX_Bot (v0.0.1)

helps you create your own bots with menus. From Games to Online Stores.

(🌐) LANG: EN, AR, RU (+10 more).(文)

👾(☰) IN MENU ⠿
Create menu, Mailing, Feedback forms, Inline menu, Macros, Commands, Referral system, Balance and Variables, Bonus, Exchange, Auto Payments and MORE

🛒IN SHOP💸
Categories, Shopping Cart, Client Profile, Order management, Payments

🎩IN AD MARKET🎭
Send Ads to over 7 Million people. Receive Ads to earn

قابل للتطوير يرجى المساهمة
    """
    await context.bot.set_my_description(description)
    await context.bot.set_my_short_description("Create your own bots with menus, shops, and ads.")
    print("✅ تم تحديث وصف البوت بنجاح")

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = get_buttons()
    if not buttons:
        await update.message.reply_text("مرحباً بك! لا توجد أزرار حالياً. استخدم /add لإضافة أول زر.")
        return
        
    keyboard = [[InlineKeyboardButton(text=name, callback_data=name)] for name in buttons.keys()]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("📋 القائمة الرئيسية:", reply_markup=reply_markup)

async def add_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        # أخذ النص بعد كلمة /add
        text = update.message.text.split('/add ', 1)[1]
        name, reply = text.split(' - ', 1)
        save_button(name.strip(), reply.strip())
        await update.message.reply_text(f"✅ تم حفظ الزر '{name.strip()}' بنجاح!")
    except Exception:
        await update.message.reply_text("❌ خطأ! استخدم الصيغة: \n/add اسم الزر - الرد")

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    buttons = get_buttons()
    if query.data in buttons:
        await query.edit_message_text(text=buttons[query.data])

# --- التشغيل الرئيسي ---
if __name__ == '__main__':
    init_db()
    
    # جلب التوكن من نظام التشغيل (للأمان في السيرفرات) أو وضعه يدوياً
    TOKEN = os.getenv('BOT_TOKEN', 'ضع_التوكن_هنا_إذا_كنت_تجرب_على_الهاتف')

    # بناء التطبيق مع إعدادات انتظار طويلة للإنترنت الضعيف
    app = Application.builder().token(TOKEN).build()

    # تحديث الوصف عند بدء التشغيل مرة واحدة
    if app.job_queue:
        app.job_queue.run_once(set_bot_description, when=0)

    # إضافة الأوامر
    app.add_handler(CommandHandler('start', start_command))
    app.add_handler(CommandHandler('add', add_button))
    app.add_handler(CallbackQueryHandler(button_click))

    print("🚀 البوت يحاول الاتصال... انتظر قليلاً")
    
    # تشغيل البوت بإعدادات "صبورة" للإنترنت الضعيف
    app.run_polling(
        poll_interval=3.0, 
        timeout=60, 
        read_timeout=60, 
        connect_timeout=60
    )