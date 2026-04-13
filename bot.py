import os
import time
import paho.mqtt.client as mqtt
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode

# ============================
# VARIABLES DE ENTORNO
# ============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 8883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

MQTT_USER = os.getenv("MQTT_USER")
MQTT_PASS = os.getenv("MQTT_PASS")

# ============================
# HANDLERS DE TELEGRAM
# ============================
def start(update, context):
    update.message.reply_text("Bot activo y escuchando MQTT.")

def estado(update, context):
    update.message.reply_text("Sistema funcionando correctamente.")

# ============================
# CALLBACKS MQTT
# ============================
def on_connect(client, userdata, flags, rc):
    print("Conectado a MQTT con código:", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    mensaje = msg.payload.decode()
    print("Mensaje MQTT recibido:", mensaje)

    from telegram import Bot
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(
        chat_id=CHAT_ID,
        text=f"📡 *MQTT:* {mensaje}",
        parse_mode=ParseMode.MARKDOWN
    )

# ============================
# MAIN
# ============================
def main():
    # Telegram
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("estado", estado))

    # MQTT
    client = mqtt.Client()
    client.tls_set()  # TLS obligatorio para HiveMQ Cloud
    client.username_pw_set(MQTT_USER, MQTT_PASS)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    # Iniciar servicios
    updater.start_polling()
    client.loop_start()

    print("Bot iniciado y escuchando MQTT...")

    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
