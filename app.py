import os
from fastapi import FastAPI, Request, HTTPException
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.environ["TELEGRAM_BOT_TOKEN"].strip()
ALLOWED_USER_ID = int(os.environ["TELEGRAM_ALLOWED_USER_ID"])
WEBHOOK_BASE_URL = os.environ["WEBHOOK_BASE_URL"].rstrip("/")
WEBHOOK_SECRET = os.environ["WEBHOOK_SECRET"].strip()

tg = Application.builder().token(BOT_TOKEN).build()
api = FastAPI(title="Tamvo AI Admin Bot")

def allowed(update: Update) -> bool:
    user = update.effective_user
    return bool(user and user.id == ALLOWED_USER_ID)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    await update.effective_message.reply_text(
        "Tamvo AI Admin Bot ishlayapti ✅\n/status - holat\n/help - yordam"
    )

async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    await update.effective_message.reply_text("✅ Tamvo AI Admin Bot online.")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not allowed(update):
        return
    await update.effective_message.reply_text(
        "Keyingi bosqichlarda: log, test, fix, deploy va rollback qo‘shamiz."
    )

tg.add_handler(CommandHandler("start", start))
tg.add_handler(CommandHandler("status", status))
tg.add_handler(CommandHandler("help", help_cmd))

@api.on_event("startup")
async def startup():
    await tg.initialize()
    await tg.start()
    await tg.bot.set_webhook(
        url=f"{WEBHOOK_BASE_URL}/telegram",
        secret_token=WEBHOOK_SECRET,
        allowed_updates=Update.ALL_TYPES,
        drop_pending_updates=True,
    )

@api.on_event("shutdown")
async def shutdown():
    await tg.stop()
    await tg.shutdown()

@api.get("/")
@api.get("/health")
async def health():
    return {"ok": True, "service": "tamvo-ai-admin"}

@api.post("/telegram")
async def telegram_webhook(request: Request):
    secret = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
    if secret != WEBHOOK_SECRET:
        raise HTTPException(status_code=403, detail="forbidden")

    payload = await request.json()
    update = Update.de_json(payload, tg.bot)
    await tg.process_update(update)
    return {"ok": True}
