import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ForceReply
from flask import Flask, request, send_file
import sqlite3
import os
from datetime import datetime
import csv

# 🧩 Configura tus variables
API_TOKEN = 'TU_BOT_TOKEN_AQUI'
WEBHOOK_URL = 'https://tudominio.com/webhook'
ADMIN_ID = 123456789  # 🔐 Reemplaza con tu ID real de Telegram

bot = telebot.TeleBot(API_TOKEN)
app = Flask(__name__)

# 🛠️ Base de datos
def init_db():
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS auditorias (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                action TEXT,
                timestamp TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS productos (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nombre TEXT,
                descripcion TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                user_id INTEGER PRIMARY KEY,
                idioma TEXT
            )
        ''')
        cursor.execute("SELECT COUNT(*) FROM productos")
        if cursor.fetchone()[0] == 0:
            cursor.execute("INSERT INTO productos (nombre, descripcion) VALUES (?, ?)",
                           ("Paracetamol", "Alivia el dolor y la fiebre"))
            cursor.execute("INSERT INTO productos (nombre, descripcion) VALUES (?, ?)",
                           ("Ibuprofeno", "Antiinflamatorio y analgésico"))
        conn.commit()

# 👁‍🗨 Verificación admin
def es_admin(user_id):
    return user_id == ADMIN_ID

# 📝 Auditoría
def registrar_auditoria(user_id, username, action):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO auditorias (user_id, username, action, timestamp) VALUES (?, ?, ?, ?)",
                       (user_id, username, action, datetime.now().isoformat()))
        conn.commit()

# 🌐 Idioma
def get_language(user_id):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT idioma FROM usuarios WHERE user_id = ?", (user_id,))
        row = cursor.fetchone()
        return row[0] if row else "es"

def set_language(user_id, lang):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT OR REPLACE INTO usuarios (user_id, idioma) VALUES (?, ?)", (user_id, lang))
        conn.commit()

# 📋 Menú
def send_menu(message):
    lang = get_language(message.from_user.id)
    is_admin = es_admin(message.from_user.id)
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    if lang == "en":
        buttons = ["💊 Show products"]
        if is_admin:
            buttons += ["Add product", "Delete product", "Statistics", "Download report"]
        text = "Choose an option:"
    else:
        buttons = ["💊 Ver productos"]
        if is_admin:
            buttons += ["Agregar producto", "Eliminar producto", "Estadísticas", "Descargar reporte"]
        text = "Elige una opción:"
    for b in buttons:
        markup.add(KeyboardButton(b))
    bot.send_message(message.chat.id, text, reply_markup=markup)

# ▶️ /start
@bot.message_handler(commands=['start'])
def handle_start(message):
    registrar_auditoria(message.from_user.id, message.from_user.username, "start")
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Español"), KeyboardButton("English"))
    bot.send_message(message.chat.id, "Elige tu idioma / Choose your language", reply_markup=markup)

# 🧠 Manejo general
@bot.message_handler(func=lambda m: True)
def handle_message(message):
    user_id = message.from_user.id
    username = message.from_user.username
    text = message.text.lower()
    lang = get_language(user_id)

    # Cambio de idioma
    if text in ["español", "spanish"]:
        set_language(user_id, "es")
        registrar_auditoria(user_id, username, "Idioma: Español")
        bot.send_message(message.chat.id, "Idioma establecido a Español.")
        send_menu(message)
    elif text in ["english", "inglés"]:
        set_language(user_id, "en")
        registrar_auditoria(user_id, username, "Language: English")
        bot.send_message(message.chat.id, "Language set to English.")
        send_menu(message)

    # Ver productos
    elif "ver productos" in text or "show products" in text:
        registrar_auditoria(user_id, username, "Ver productos")
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT nombre, descripcion FROM productos")
            productos = cursor.fetchall()
        for nombre, descripcion in productos:
            bot.send_message(message.chat.id, f"💊 *{nombre}*\n📝 {descripcion}", parse_mode='Markdown')

    # Agregar producto (admin)
    elif text in ["agregar producto", "add product"] and es_admin(user_id):
        prompt = "Nombre del producto:" if lang == "es" else "Product name:"
        msg = bot.send_message(message.chat.id, prompt, reply_markup=ForceReply())
        bot.register_next_step_handler(msg, recibir_nombre_producto)

    # Eliminar producto (admin)
    elif text in ["eliminar producto", "delete product"] and es_admin(user_id):
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT id, nombre FROM productos")
            productos = cursor.fetchall()
        if not productos:
            msg = "No hay productos." if lang == "es" else "No products found."
            bot.send_message(message.chat.id, msg)
        else:
            lista = "\n".join([f"{p[0]} - {p[1]}" for p in productos])
            prompt = "Escribe el ID del producto a eliminar:" if lang == "es" else "Enter the product ID to delete:"
            bot.send_message(message.chat.id, lista)
            msg = bot.send_message(message.chat.id, prompt, reply_markup=ForceReply())
            bot.register_next_step_handler(msg, eliminar_producto)

    # Estadísticas (admin)
    elif text in ["estadísticas", "statistics"] and es_admin(user_id):
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM usuarios")
            total_usuarios = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM auditorias")
            total_auditorias = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM productos")
            total_productos = cursor.fetchone()[0]
        if lang == "es":
            msg = f"📊 Estadísticas:\nUsuarios: {total_usuarios}\nAuditorías: {total_auditorias}\nProductos: {total_productos}"
        else:
            msg = f"📊 Statistics:\nUsers: {total_usuarios}\nAudits: {total_auditorias}\nProducts: {total_productos}"
        registrar_auditoria(user_id, username, "Ver estadísticas")
        bot.send_message(message.chat.id, msg)

    # Reporte CSV
    elif text in ["descargar reporte", "download report"] and es_admin(user_id):
        registrar_auditoria(user_id, username, "Descargar CSV")
        url = f"{WEBHOOK_URL}/download_audits/{ADMIN_ID}"
        msg = "📥 Haz clic para descargar el reporte CSV:\n" if lang == "es" else "📥 Click to download CSV report:\n"
        bot.send_message(message.chat.id, msg + url)

    else:
        mensaje = "Comando no reconocido." if lang == "es" else "Command not recognized."
        bot.send_message(message.chat.id, mensaje)

# ➕ Agregar producto paso a paso
def recibir_nombre_producto(message):
    nombre = message.text
    bot.send_message(message.chat.id, "Descripción del producto:")
    bot.register_next_step_handler(message, lambda msg: guardar_producto(msg, nombre))

def guardar_producto(message, nombre):
    descripcion = message.text
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO productos (nombre, descripcion) VALUES (?, ?)", (nombre, descripcion))
        conn.commit()
    registrar_auditoria(message.from_user.id, message.from_user.username, f"Agregó producto: {nombre}")
    lang = get_language(message.from_user.id)
    bot.send_message(message.chat.id, "Producto guardado." if lang == "es" else "Product saved.")

# ❌ Eliminar producto
def eliminar_producto(message):
    try:
        id_producto = int(message.text.strip())
        with sqlite3.connect('database.db') as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM productos WHERE id = ?", (id_producto,))
            conn.commit()
        registrar_auditoria(message.from_user.id, message.from_user.username, f"Eliminó producto {id_producto}")
        lang = get_language(message.from_user.id)
        bot.send_message(message.chat.id, "Producto eliminado." if lang == "es" else "Product deleted.")
    except Exception:
        bot.send_message(message.chat.id, "ID inválido.")

# 🌐 Webhook Flask
@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return '', 200

@app.route('/set_webhook', methods=['GET'])
def set_webhook():
    bot.remove_webhook()
    bot.set_webhook(url=WEBHOOK_URL)
    return "Webhook configurado."

# 📤 Descargar CSV
@app.route('/download_audits/<admin_id>', methods=['GET'])
def download_audits(admin_id):
    if str(ADMIN_ID) != admin_id:
        return "No autorizado", 403
    filename = 'auditorias.csv'
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM auditorias")
        rows = cursor.fetchall()
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['ID', 'User ID', 'Username', 'Action', 'Timestamp'])
        writer.writerows(rows)
    return send_file(filename, as_attachment=True)

# ▶️ Main
if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
