import os
import time
import json
import paho.mqtt.client as mqtt
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode, Bot

# ============================
# VARIABLES DE ENTORNO
# ============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

MQTT_COMMAND_TOPIC = os.getenv("MQTT_COMMAND_TOPIC", "acuario/comandos")

mqtt_client = None

# ============================
# VARIABLES PARA TIMEOUT /ESTADO
# ============================
esperando_respuesta = False
chat_id_estado = None


# ============================
# HANDLERS DE TELEGRAM
# ============================
def start(update, context):
    update.message.reply_text("Bot activo y escuchando MQTT.")


def estado(update, context):
    global esperando_respuesta, chat_id_estado

    esperando_respuesta = True
    chat_id_estado = update.message.chat_id

    update.message.reply_text("Consultando estado del dispositivo...")

    if mqtt_client:
        mqtt_client.publish(MQTT_COMMAND_TOPIC, "estado")

    # Timeout de 3 segundos
    context.job_queue.run_once(verificar_timeout, 3, context=chat_id_estado)


def verificar_timeout(context):
    global esperando_respuesta

    if esperando_respuesta:
        esperando_respuesta = False
        context.bot.send_message(
            chat_id=context.job.context,
            text="⚠️ El dispositivo no está conectado o no responde."
        )


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
    global esperando_respuesta

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
        sensor = "Desconocido"
        nivel = "N/A"
        tipo = "Mensaje simple"
        mensaje = mensaje_raw
        data = {}

    # Fecha y hora actual
    from datetime import datetime
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    bot = Bot(token=TELEGRAM_TOKEN)

    # ============================
    # RESPUESTA ESPECIAL PARA /ESTADO
    # ============================
    if esperando_respuesta and tipo == "Estado":
        esperando_respuesta = False

        # Tiempo total de funcionamiento
        try:
            tiempo_ms = int(data.get("tiempo_total_bomba_ms", 0))
            minutos_bomba = round(tiempo_ms / 60000, 2)
        except:
            minutos_bomba = "N/A"

        # Última vez encendida
        try:
            ultima = int(data.get("ultima_vez_encendida", 0))
            if ultima > 0:
                ultima_min = round((time.time()*1000 - ultima) / 60000, 2)
                ultima_texto = f"Hace {ultima_min} min"
            else:
                ultima_texto = "Nunca"
        except:
            ultima_texto = "N/A"

        texto_estado = (
            f"🐠 *Estado del Sistema Acuario*\n"
            f"📅 *Fecha:* {fecha}\n\n"
            f"📍 *Sensor:* {sensor}\n"
            f"💧 *Nivel del agua:* {nivel}\n"
            f"🔌 *Bomba:* {data.get('bomba', 'N/A')}\n"
            f"🛠️ *Mantenimiento:* {data.get('mantenimiento', 'N/A')}\n"
            f"🚨 *Falla:* {data.get('falla', 'N/A')}\n\n"
            f"📡 *WiFi RSSI:* {data.get('wifi_rssi', 'N/A')} dBm\n"
            f"⏱️ *Tiempo total bomba:* {minutos_bomba} min\n"
            f"⏳ *Última vez encendida:* {ultima_texto}\n"
            f"🔘 *Estado del relé:* {data.get('rele', 'N/A')}"
        )

        bot.send_message(
            chat_id=CHAT_ID,
            text=texto_estado,
            parse_mode="Markdown"
        )
        return

    # ============================
    # MENSAJES NORMALES
    # ============================
    texto = (
        f"🐠 *Sistema Acuario*\n"
        f"📅 *Fecha:* {fecha}\n"
        f"📍 *Sensor:* {sensor}\n"
        f"💧 *Nivel del agua:* {nivel}\n"
        f"⚠️ *Tipo de alerta:* {tipo}\n"
        f"🔔 *Mensaje:* {mensaje}"
    )

    bot.send_message(
        chat_id=CHAT_ID,
        text=texto,
        parse_mode="Markdown"
    )


import os
import time
import json
import paho.mqtt.client as mqtt
from telegram.ext import Updater, CommandHandler
from telegram import ParseMode, Bot

# ============================
# VARIABLES DE ENTORNO
# ============================
TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")

MQTT_BROKER = os.getenv("MQTT_BROKER")
MQTT_PORT = int(os.getenv("MQTT_PORT", 1883))
MQTT_TOPIC = os.getenv("MQTT_TOPIC")

MQTT_COMMAND_TOPIC = os.getenv("MQTT_COMMAND_TOPIC", "acuario/comandos")

mqtt_client = None

# ============================
# VARIABLES PARA TIMEOUT /ESTADO
# ============================
esperando_respuesta = False
chat_id_estado = None


# ============================
# HANDLERS DE TELEGRAM
# ============================
def start(update, context):
    update.message.reply_text("Bot activo y escuchando MQTT.")


def estado(update, context):
    global esperando_respuesta, chat_id_estado

    esperando_respuesta = True
    chat_id_estado = update.message.chat_id

    update.message.reply_text("Consultando estado del dispositivo...")

    if mqtt_client:
        mqtt_client.publish(MQTT_COMMAND_TOPIC, "estado")

    context.job_queue.run_once(verificar_timeout, 3, context=chat_id_estado)


def verificar_timeout(context):
    global esperando_respuesta

    if esperando_respuesta:
        esperando_respuesta = False
        context.bot.send_message(
            chat_id=context.job.context,
            text="⚠️ El dispositivo no está conectado o no responde."
        )


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


def llenar(update, context):
    update.message.reply_text("🚰 Iniciando modo llenado (comando enviado por MQTT).")
    if mqtt_client:
        mqtt_client.publish(MQTT_COMMAND_TOPIC, "llenar")


# ============================
# CALLBACKS MQTT
# ============================
def on_connect(client, userdata, flags, rc):
    print("Conectado a MQTT con código:", rc)
    client.subscribe(MQTT_TOPIC)


def on_message(client, userdata, msg):
    global esperando_respuesta

    mensaje_raw = msg.payload.decode()
    print("Mensaje MQTT recibido:", mensaje_raw)

    try:
        data = json.loads(mensaje_raw)
        sensor = data.get("sensor", "Desconocido")
        nivel = data.get("nivel", "N/A")
        tipo = data.get("tipo", "N/A")
        mensaje = data.get("mensaje", mensaje_raw)
    except:
        sensor = "Desconocido"
        nivel = "N/A"
        tipo = "Mensaje simple"
        mensaje = mensaje_raw
        data = {}

    from datetime import datetime
    fecha = datetime.now().strftime("%Y-%m-%d %H:%M")

    bot = Bot(token=TELEGRAM_TOKEN)

    # ============================
    # RESPUESTA ESPECIAL PARA /ESTADO
    # ============================
    if esperando_respuesta and tipo == "Estado":
        esperando_respuesta = False

        try:
            tiempo_ms = int(data.get("tiempo_total_bomba_ms", 0))
            minutos_bomba = round(tiempo_ms / 60000, 2)
        except:
            minutos_bomba = "N/A"

        try:
            ultima = int(data.get("ultima_vez_encendida", 0))
            if ultima > 0:
                ultima_min = round((time.time()*1000 - ultima) / 60000, 2)
                ultima_texto = f"Hace {ultima_min} min"
            else:
                ultima_texto = "Nunca"
        except:
            ultima_texto = "N/A"

        texto_estado = (
            f"🐠 *Estado del Sistema Acuario*\n"
            f"📅 *Fecha:* {fecha}\n\n"
            f"📍 *Sensor:* {sensor}\n"
            f"💧 *Nivel del agua:* {nivel}\n"
            f"🔌 *Bomba:* {data.get('bomba', 'N/A')}\n"
            f"🛠️ *Mantenimiento:* {data.get('mantenimiento', 'N/A')}\n"
            f"🚨 *Falla:* {data.get('falla', 'N/A')}\n\n"
            f"📡 *WiFi RSSI:* {data.get('wifi_rssi', 'N/A')} dBm\n"
            f"⏱️ *Tiempo total bomba:* {minutos_bomba} min\n"
            f"⏳ *Última vez encendida:* {ultima_texto}\n"
            f"🔘 *Estado del relé:* {data.get('rele', 'N/A')}"
        )

        bot.send_message(
            chat_id=CHAT_ID,
            text=texto_estado,
            parse_mode="Markdown"
        )
        return

    # ============================
    # MENSAJE ESPECIAL: BLOQUEADO POR MANTENIMIENTO
    # ============================
    if tipo == "Bloqueado":
        texto_bloqueo = (
            f"🔧 *Modo mantenimiento activo*\n"
            f"📅 *Fecha:* {fecha}\n\n"
            f"🚫 *Comando bloqueado por interruptor físico*\n"
            f"🔔 *Mensaje:* {mensaje}"
        )

        bot.send_message(
            chat_id=CHAT_ID,
            text=texto_bloqueo,
            parse_mode="Markdown"
        )
        return

    # ============================
    # MENSAJES NORMALES
    # ============================
    texto = (
        f"🐠 *Sistema Acuario*\n"
        f"📅 *Fecha:* {fecha}\n"
        f"📍 *Sensor:* {sensor}\n"
        f"💧 *Nivel del agua:* {nivel}\n"
        f"⚠️ *Tipo de alerta:* {tipo}\n"
        f"🔔 *Mensaje:* {mensaje}"
    )

    bot.send_message(
        chat_id=CHAT_ID,
        text=texto,
        parse_mode="Markdown"
    )


# ============================
# MAIN
# ============================
def main():
    global mqtt_client

    updater = Updater(TELEGRAM_TOKEN, use_context=True)
    dp = updater.dispatcher

    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("estado", estado))
    dp.add_handler(CommandHandler("encender", encender))
    dp.add_handler(CommandHandler("apagar", apagar))
    dp.add_handler(CommandHandler("reset", reset_cmd))
    dp.add_handler(CommandHandler("llenar", llenar))

    client = mqtt.Client()
    mqtt_client = client

    client.reconnect_delay_set(min_delay=1, max_delay=30)
    client.on_connect = on_connect
    client.on_message = on_message

    client.connect(MQTT_BROKER, MQTT_PORT, keepalive=20)

    updater.start_polling()
    client.loop_start()

    print("Bot iniciado y escuchando MQTT...")

    while True:
        time.sleep(1)


if __name__ == "__main__":
    main()
