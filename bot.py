import os
import time
import paho.mqtt.client as mqtt
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode

TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

def start(update, context):
    update.message.reply_text("Bot activo y escuchando MQTT.")

def estado(update, context):
    update.message.reply_text("Sistema funcionando correctamente.")

def on_connect(client, userdata, flags, rc):
    print("Conectado a MQTT con código:", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    mensaje = msg.payload.decode()
    print("Mensaje MQTT recibido:", mensaje)

    from telegram import Bot
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(chat_id=CHAT_ID, text=f"📡 *MQTT:* {mensaje}", parse_mode=ParseMode.MARKDOWN)

def main():
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("estado", estado))

    client = mqtt.Client()
    client.on_connect = on_connect
    client.on_message = on_message
    client.connect(MQTT_BROKER, MQTT_PORT, 60)

    updater.start_polling()
    client.loop_start()

    print("Bot iniciado")
    while True:
        time.sleep(1)

if __name__ == "__main__":
    main()
