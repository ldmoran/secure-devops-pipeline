import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

# TOKEN
BOT_TOKEN = "8620126753:AAHQoU_jR-JaYk55yyvyk6gAPTOs2gpwtDI"

#  TU API EN RENDER
API_URL = "https://secure-devops-pipeline.onrender.com/predict"


def analizar_codigo(code):
    try:
        response = requests.post(API_URL, json={"code": code})
        return response.json()
    except Exception as e:
        return {"error": str(e)}


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    code = update.message.text

    result = analizar_codigo(code)

    if "error" in result:
        await update.message.reply_text(f"❌ Error: {result['error']}")
        return

    respuesta = f"""
🔍 RESULTADO:

🧠 Predicción: {result['prediction']}
📊 Confianza: {result['confidence']:.2f}

SEGURO: {result['probabilities']['SEGURO']:.2f}
VULNERABLE: {result['probabilities']['VULNERABLE']:.2f}
"""

    await update.message.reply_text(respuesta)


def main():
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Bot corriendo...")
    app.run_polling()


if __name__ == "__main__":
    main()