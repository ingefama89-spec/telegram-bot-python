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
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

# Topic para enviar comandos al ESP8266
MQTT_COMMAND_TOPIC = os.getenv("MQTT_COMMAND_TOPIC", "acuario/comandos")

# Cliente MQTT global para usar dentro de los comandos
mqtt_client = None


# ============================
# HANDLERS DE TELEGRAM
# ============================
def start(update, context):
    update.message.reply_text("Bot activo y escuchando MQTT.")

def estado(update, context):
    update.message.reply_text("Sistema funcionando correctamente.")

def encender(update, context):
    update.message.reply_text("🔌 Encendiendo bomba (comando enviado por MQTT).")
    if mqtt_client:
        mqtt_client.publish(MQTT_COMMAND_TOPIC, "encender")

def apagar(update, context):
    update.message.reply_text("⛔ Apagando bomba (comando enviado por MQTT).")
    if mqtt_client:
        mqtt_client.publish(MQTT_COMMAND_TOPIC, "apagar")

def reset_cmd(update, context):
    update.message.reply_text("♻️ Reset de fallas solicitado (enviado por MQTT).")
    if mqtt_client:
        mqtt_client.publish(MQTT_COMMAND_TOPIC, "reset")


# ============================
# CALLBACKS MQTT
# ============================
def on_connect(client, userdata, flags, rc):
    print("Conectado a MQTT con código:", rc)
    client.subscribe(MQTT_TOPIC)

def on_message(client, userdata, msg):
    import json
    from datetime import datetime

    mensaje_raw = msg.payload.decode()
    print("Mensaje MQTT recibido:", mensaje_raw)

    # Intentar parsear JSON
    try:
        data = json.loads(mensaje_raw)
        sensor = data.get("sensor", "Desconocido")
        nivel = data.get("nivel", "N/A")
        tipo = data.get("tipo", "N/A")
        mensaje = data.get("mensaje", mensaje_raw)
    except:
        # Si no es JSON, enviar texto plano
        sensor = "Desconocido"
        nivel = "N/A"
        tipo = "Mensaje simple"
        mensaje = mensaje_raw

    # Fecha y hora actual
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    texto = (
        f"🐠 *Sistema Acuario*\n"
        f"📅 *Fecha:* {fecha}\n"
        f"📍 *Sensor:* {sensor}\n"
        f"💧 *Nivel del agua:* {nivel}\n"
        f"⚠️ *Tipo de alerta:* {tipo}\n"
        f"🔔 *Mensaje:* {mensaje}"
    )

    from telegram import Bot
    bot = Bot(token=TELEGRAM_TOKEN)
    bot.send_message(
        chat_id=CHAT_ID,
        text=texto,
        parse_mode="Markdown"
    )


# ============================
# MAIN
# ============================
def main():
    global mqtt_client  # para que los handlers puedan usarlo

    # Telegram
    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    # Registrar comandos
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("estado", estado))
    dp.add_handler(CommandHandler("encender", encender))
    dp.add_handler(CommandHandler("apagar", apagar))
    dp.add_handler(CommandHandler("reset", reset_cmd))

    # MQTT
    client = mqtt.Client()
    mqtt_client = client  # guardar referencia global

    client.reconnect_delay_set(min_delay=1, max_delay=30)

    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=20)

    # Iniciar servicios
    updater.start_polling()
    client.loop_start()

    print("Bot iniciado y escuchando MQTT...")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
