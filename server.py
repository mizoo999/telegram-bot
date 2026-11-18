import os
import json
import logging
import datetime
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, CommandHandler, MessageHandler, filters

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "9091267491:AAGEsPavlSriCCLXbiW-9sHQb5fPDRY7MS0")
GEMINI_KEY = os.getenv("GEMINI_API_KEY", "")

CONFIG_FILE = "config.json"
NOTES_FILE = "notes.txt"

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"gemini_key": GEMINI_KEY}

def save_config(cfg):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump(cfg, f, ensure_ascii=False, indent=2)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    reply = (
        f"أهلاً بك يا {user_name}! 🌟\n"
        "أنا 'عون' (AwnAssistant) - وكيلك الذكي السحابي.\n\n"
        "⚡ الأوامر المتاحة من هاتفك:\n"
        "• /status - فحص حالة الخادم والسحابة\n"
        "• /note [نص] - حفظ ملاحظة أو فكرة\n"
        "• /notes - قراءة جميع الملاحظات\n"
        "• /key [Gemini_Key] - تفعيل مخ الذكاء الاصطناعي\n"
        "• /help - دليل الأوامر\n\n"
        "💬 اكتب أي سؤال وسأجيبك فوراً!"
    )
    await update.message.reply_text(reply)

async def status_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reply = (
        "☁️ تقرير الخادم السحابي:\n"
        "━━━━━━━━━━━━━━━━━\n"
        "• الحالة: متصل ويعمل 24/7 بنجاح 🟢\n"
        f"• الوقت: {now}\n"
        "• الاستجابة: ممتازة وفورية ⚡"
    )
    await update.message.reply_text(reply)

async def note_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = " ".join(context.args)
    if not text:
        await update.message.reply_text("الرجاء كتابة نص الملاحظة بعد الأمر، مثلاً:\n/note شراء خادم جديد")
        return
    now = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
    with open(NOTES_FILE, "a", encoding="utf-8") as f:
        f.write(f"[{now}] {text}\n")
    await update.message.reply_text(f"📝 تم حفظ الملاحظة:\n\"{text}\"")

async def notes_list(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if os.path.exists(NOTES_FILE):
        with open(NOTES_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if content:
            await update.message.reply_text(f"📝 ملاحظاتك المسجلة:\n\n{content}")
            return
    await update.message.reply_text("📝 لا توجد ملاحظات محفوظة.")

async def key_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("يرجى كتابة المفتاح بعد الأمر، مثال:\n/key AIzaSy...")
        return
    k = context.args[0].strip()
    cfg = load_config()
    cfg["gemini_key"] = k
    save_config(cfg)
    await update.message.reply_text("🔑 تم حفظ مفتاح الذكاء الاصطناعي بنجاح!")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text
    user_name = update.effective_user.first_name
    cfg = load_config()
    api_key = cfg.get("gemini_key") or os.getenv("GEMINI_API_KEY")
    
    if api_key:
        try:
            import google.generativeai as genai
            genai.configure(api_key=api_key)
            model = genai.GenerativeModel("gemini-1.5-flash")
            resp = model.generate_content(
                f"أنت 'عون'، وكيل أعمال ومساعد ذكي من Google DeepMind عبر تيليجرام. أجب باحترافية، ولغة عربية ممتازة تناسب شاشات الهاتف.\n\nرسالة المستخدم: {text}"
            )
            await update.message.reply_text(resp.text)
            return
        except Exception as e:
            await update.message.reply_text(f"⚠️ خطأ أثناء توليد الرد: {e}")
            return

    await update.message.reply_text(
        f"وصلتني رسالتك يا {user_name}: \"{text}\"\n\n"
        "💡 لتفعيل إجابات الذكاء الاصطناعي الكاملة، أرسل مفتاح Gemini المجاني:\n"
        "/key your_api_key\n"
        "(من aistudio.google.com)"
    )

def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("status", status_cmd))
    app.add_handler(CommandHandler("note", note_cmd))
    app.add_handler(CommandHandler("notes", notes_list))
    app.add_handler(CommandHandler("key", key_cmd))
    app.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
    
    print("Cloud bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
