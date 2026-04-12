import os
import time
import paho.mqtt.client as mqtt
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode

# ============================
# VARIABLES DE ENTORNO
# ============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")  # ID del chat donde enviar alertas
MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

# ============================
# TELEGRAM - COMANDOS
# ============================

def start(update, context):
    update.message.reply_text("🤖 Bot activo y escuchando MQTT.")

def estado(update, context):
    update.message.reply_text("📡 Sistema funcionando correctamente.")

def temperatura(update, context):
    update.message.reply_text("🌡️ Consultando temperatura...")

def ph(update, context):
    update.message.reply_text("🧪 Consultando pH...")

def reiniciar(update, context):
    update.message.reply_text("🔄 Reiniciando sistema (simulado).")

# ============================
# MQTT - CALLBACKS
# ============================

def on_connect(client, userdata, flags, rc):
    print("Conectado a MQTT con código:", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    mensaje = msg.payload.decode()
    print(f"MQTT recibido: {mensaje}")

    # Enviar a Telegram
    try:
        context = userdata["context"]
        context.bot.send_message(
            chat_id=CHAT_ID,
            text=f"🚨 *ALERTA MQTT*\n\nMensaje: `{mensaje}`",
            parse_mode=ParseMode.MARKDOWN
        )
    except Exception as e:
        print("Error enviando a Telegram:", e)

# ============================
# MAIN
# ============================

def main():
    # Telegram
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Registrar comandos
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("estado", estado))
    dp.add_handler(CommandHandler("temperatura", temperatura))
    dp.add_handler(CommandHandler("ph", ph))
    dp.add_handler(CommandHandler("reiniciar", reiniciar))

    # MQTT
    client = mqtt.Client(userdata={"context": updater.bot})
    client.on_connect = on_connect
    client.on_message = on_message

    # Conectar MQTT
    while True:
        try:
            client.connect(MQTT_BROKER, MQTT_PORT, 60)
            break
        except Exception as e:
            print("Error conectando MQTT, reintentando:", e)
            time.sleep(5)

    # Iniciar hilos
    client.loop_start()
    updater.start_polling()
    updater.idle()

if __name__ == "__main__":
    main()
# fuerza deploy
