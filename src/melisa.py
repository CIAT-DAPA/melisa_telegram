import os
import re
from flask import Flask, request, Response
import requests
import telegram
from datetime import datetime
import uuid

app = Flask(__name__)

FOLDER_APP = "/var/www/melisa/telegram/"
FILE_TOKEN = FOLDER_APP + "token.txt"
FILE_TOKEN_DEMETER = FOLDER_APP + "token_demeter.txt"
TOKEN = ""
with open(FILE_TOKEN, "r") as f:
    TOKEN = f.read()
MELISA_NAME = "telegram"
TOKEN_DEMETER = ""
DEMETER_URL = "https://demeter.aclimate.org/api/v1/query/"

URL = "https://melisatg.aclimate.org/"
BOT_USER_NAME = "Melisa_chatbot"
bot = None

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

            # Envia la información a Demeter u realiza otras acciones necesarias
            # ...

            # Devuelve la misma imagen como respuesta
            update.message.reply_photo(photo.file_id)
            print("Imagen guardada exitosamente")

    except Exception as e:
        print(f"Error: {e}")

@app.route('/')
def index():
    return '<h1>Running MelisaBot for Telegram</h1>'

@app.route('/set_webhook', methods=['GET', 'POST'])
def set_webhook():
    s = bot.setWebhook('{URL}{HOOK}'.format(URL=URL, HOOK=TOKEN))
    if s:
        return "webhook setup ok"
    else:
        return "webhook setup failed"

@app.route('/{}'.format(TOKEN), methods=['POST'])
def respond():
    # retrieve the message in JSON and then transform it to a Telegram object
    update = telegram.Update.de_json(request.get_json(force=True), bot)

    sender_id = str(update.message.chat.id)
    ext_id = str(update.message.message_id)

    try:
        if update.message.photo:
            # Llama a la función para manejar imágenes
            handle_image(update, None)
        else:
            # Procesa mensajes de texto
            text = update.message.text.encode('utf-8').decode()
            text = re.sub(r"\W", "_", text)
            if text != "/start":
                json_data = {"melisa": MELISA_NAME, "token": TOKEN_DEMETER, "user": sender_id, "chat_id": ext_id, "message": text}
                r = requests.post(DEMETER_URL, json=json_data)

    except Exception as e:
        print(f"Error: {e}")

    return Response('ok', 200)

@app.route("/receptor", methods=['POST'])
def receptor():
    data = request.get_json()
    token = data['token']
    messages = data['text']
    sender_id = data['user_id']
    chat_id = data['chat_id'] if 'chat_id' in data else None
    first = True

    if token == TOKEN_DEMETER:
        for m in messages:
            if first and chat_id is not None:
                bot.sendMessage(chat_id=sender_id, text=m, reply_to_message_id=chat_id)
                first = False
            else:
                bot.sendMessage(chat_id=sender_id, text=m)

    return Response('ok', 200)

if __name__ == '__main__':
    with open(FILE_TOKEN_DEMETER, "r") as f:
        TOKEN_DEMETER = f.read()

    bot = telegram.Bot(token=TOKEN)

    # app.run(threaded=True, port=5000)
    app.run(host='0.0.0.0', port=5001)
    print("Start server on PORT 5001")
