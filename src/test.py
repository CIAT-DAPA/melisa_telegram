import os
from datetime import datetime
import uuid
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters

# Función que maneja el comando /start
def start(update, context):
    update.message.reply_text("Hola! Soy tu bot de Telegram. ¡Envíame un mensaje!")

# Función que maneja los mensajes de texto
def echo(update, context):
    update.message.reply_text(update.message.text)

# Función que maneja las imágenes
def handle_image(update, context):
    try:
        # Verifica si el mensaje contiene una foto
        print("Mensaje de foto recibido")
        if update.message.photo:
            # Obtiene el objeto de la foto más grande
            photo = update.message.photo[-1]

            # Obtiene el identificador único del usuario
            user_id = update.message.from_user.id

            # Genera un nombre único para la imagen basado en un UUID
            file_id = str(uuid.uuid4())

            # Obtiene la fecha actual en formato YYYYMMDD
            date_today = datetime.now().strftime("%Y%m%d")

            # Crea el directorio si no existe
            user_dir = os.path.join(".//images", date_today, str(user_id))
            os.makedirs(user_dir, exist_ok=True)

            # Guarda la imagen en el directorio correspondiente
            file_path = os.path.join(user_dir, f"{file_id}.jpg")
            photo.get_file().download(file_path)

            # Devuelve la misma imagen como respuesta
            update.message.reply_photo(photo.file_id)
            print("Imagen guardada exitosamente")

    except Exception as e:
        print(f"Error: {e}")

def main():
    # Reemplaza 'TU_TOKEN' con el token que obtuviste del BotFather
    updater = Updater(token='6754376727:AAGw1zpPpPlDzFSHRS8kadnXqNjStWGGzgA', use_context=True)

    # Obtiene el despachador para registrar manejadores
    dp = updater.dispatcher

    # Registra el manejador para el comando /start
    dp.add_handler(CommandHandler("start", start))

    # Registra el manejador para mensajes de texto
    dp.add_handler(MessageHandler(Filters.text & ~Filters.command, echo))

    # Registra el manejador para manejar imágenes
    dp.add_handler(MessageHandler(Filters.photo, handle_image))

    # Inicia el bot
    updater.start_polling()

    # Detiene el bot si se presiona Ctrl+C
    updater.idle()

if __name__ == '__main__':
    main()
