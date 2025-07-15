import telebot
from telebot.types import ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove, ForceReply
from flask import Flask, request, send_file
import sqlite3
import os
from datetime import datetime
import csv

API_TOKEN = '7504345200:AAFl3uHBy3Qw0ZUW8INGrnoZamxcwjKe_lc'
ADMIN_ID = 123456789  # Cambia por tu ID de admin

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
                descripcion TEXT,
                precio REAL
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS usuarios (
                user_id INTEGER PRIMARY KEY,
                idioma TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ordenes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                productos TEXT,
                direccion TEXT,
                total REAL
            )
        ''')

        # Productos naturales por defecto
        cursor.execute("SELECT COUNT(*) FROM productos")
        if cursor.fetchone()[0] == 0:
            productos = [
                ("Té de manzanilla", "Relajante natural", 2.5),
                ("Infusión de menta", "Alivia malestares digestivos", 2.0),
                ("Té de jengibre y limón", "Refuerza sistema inmune", 3.0),
                ("Infusión de frutos rojos", "Antioxidante", 3.5),
                ("Té verde", "Energizante natural", 2.8),
            ]
            cursor.executemany("INSERT INTO productos (nombre, descripcion, precio) VALUES (?, ?, ?)", productos)
        conn.commit()

# 📒 Utilidades
def es_admin(user_id):
    return user_id == ADMIN_ID

def registrar_auditoria(user_id, username, action):
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO auditorias (user_id, username, action, timestamp) VALUES (?, ?, ?, ?)",
                       (user_id, username, action, datetime.now().isoformat()))
        conn.commit()

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

# 🚀 Iniciar
@bot.message_handler(commands=['start'])
def start(message):
    markup = ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add(KeyboardButton("Español"), KeyboardButton("English"))
    bot.send_message(message.chat.id, "Elige tu idioma / Choose your language", reply_markup=markup)

@bot.message_handler(func=lambda m: m.text in ["Español", "English"])
def seleccionar_idioma(message):
    lang = "es" if message.text == "Español" else "en"
    set_language(message.from_user.id, lang)
    registrar_auditoria(message.from_user.id, message.from_user.username, f"Idioma: {lang}")
    mostrar_productos(message)

# 🍵 Mostrar productos para elegir
def mostrar_productos(message):
    lang = get_language(message.from_user.id)
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id, nombre FROM productos")
        productos = cursor.fetchall()

    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    for pid, nombre in productos:
        markup.add(KeyboardButton(f"{nombre}"))
    markup.add(KeyboardButton("✅ Finalizar selección"))

    msg = "Selecciona los productos naturales que deseas:" if lang == "es" else "Select the natural products you want:"
    bot.send_message(message.chat.id, msg, reply_markup=markup)
    bot.register_next_step_handler(message, recolectar_productos, [])

def recolectar_productos(message, seleccionados):
    lang = get_language(message.from_user.id)

    if message.text == "✅ Finalizar selección":
        if not seleccionados:
            bot.send_message(message.chat.id, "No seleccionaste ningún producto." if lang == "es" else "You didn't select any product.")
            return mostrar_productos(message)
        else:
            productos_str = ", ".join(seleccionados)
            bot.send_message(message.chat.id, "📍 Ingresa tu dirección de envío:" if lang == "es" else "📍 Enter your delivery address:", reply_markup=ForceReply())
            bot.register_next_step_handler(message, pedir_direccion, productos_str)
            return

    seleccionados.append(message.text)
    bot.send_message(message.chat.id, f"🟢 Agregado: {message.text}")
    bot.register_next_step_handler(message, recolectar_productos, seleccionados)

def pedir_direccion(message, productos_str):
    direccion = message.text
    user_id = message.from_user.id
    lang = get_language(user_id)

    total = calcular_total(productos_str)
    total_con_iva = round(total * 1.15, 2)

    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        cursor.execute("INSERT INTO ordenes (user_id, productos, direccion, total) VALUES (?, ?, ?, ?)",
                       (user_id, productos_str, direccion, total_con_iva))
        conn.commit()

    mensaje = (
        f"📟 Resumen de compra:\n{productos_str}\n📍 Dirección: {direccion}\n💵 Total con IVA (15%): ${total_con_iva}\n\n¡Gracias por tu compra! 🌿"
        if lang == "es" else
        f"📟 Order summary:\n{productos_str}\n📍 Address: {direccion}\n💵 Total with VAT (15%): ${total_con_iva}\n\nThanks for your purchase! 🌿"
    )
    bot.send_message(message.chat.id, mensaje, reply_markup=ReplyKeyboardRemove())
    registrar_auditoria(user_id, message.from_user.username, "Compra realizada")

def calcular_total(productos_str):
    nombres = [p.strip() for p in productos_str.split(",")]
    total = 0
    with sqlite3.connect('database.db') as conn:
        cursor = conn.cursor()
        for nombre in nombres:
            cursor.execute("SELECT precio FROM productos WHERE nombre = ?", (nombre,))
            row = cursor.fetchone()
            if row:
                total += row[0]
    return total

# CSV y admin
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

@app.route('/webhook', methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.get_data().decode("utf-8"))
    bot.process_new_updates([update])
    return '', 200

@app.route('/')
def home():
    return 'Bot funcionando localmente'

if __name__ == '__main__':
    init_db()
    bot.polling()
