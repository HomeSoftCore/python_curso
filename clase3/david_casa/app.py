from flask import Flask, render_template
import requests

app = Flask(__name__)

@app.route("/")
def mostrar_personajes():
    url = "https://rickandmortyapi.com/api/character"
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        personajes = data["results"]  # Lista de personajes
    else:
        personajes = []

    return render_template("personajes.html", personajes=personajes)

if __name__ == "__main__":
    app.run(debug=True)
