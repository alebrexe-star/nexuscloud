from flask import Flask, render_template, request, redirect
import os, zipfile, subprocess

app = Flask(__name__)

BASE = os.path.dirname(os.path.abspath(__file__))
BOTS = os.path.join(BASE, "bots")
UPLOADS = os.path.join(BASE, "uploads")

os.makedirs(BOTS, exist_ok=True)
os.makedirs(UPLOADS, exist_ok=True)

processos = {}

def find_bot_file(path):
    if os.path.exists(os.path.join(path, "main.py")):
        return "main.py"
    if os.path.exists(os.path.join(path, "bot.py")):
        return "bot.py"
    return None

@app.route("/")
def home():
    return render_template("index.html", bots=os.listdir(BOTS))

@app.route("/upload", methods=["POST"])
def upload():
    file = request.files["file"]

    zip_path = os.path.join(UPLOADS, file.filename)
    file.save(zip_path)

    name = file.filename.replace(".zip", "")
    path = os.path.join(BOTS, name)

    os.makedirs(path, exist_ok=True)

    with zipfile.ZipFile(zip_path, "r") as z:
        z.extractall(path)

    return redirect("/")

@app.route("/start/<bot>")
def start(bot):
    path = os.path.join(BOTS, bot)
    file = find_bot_file(path)

    if not file:
        return "bot.py ou main.py não encontrado"

    full = os.path.join(path, file)

    log = open(os.path.join(path, "log.txt"), "w")

    p = subprocess.Popen(
        ["python3", full],
        stdout=log,
        stderr=subprocess.STDOUT
    )

    processos[bot] = p

    return redirect("/")

@app.route("/restart/<bot>")
def restart(bot):
    if bot in processos:
        try:
            processos[bot].kill()
        except:
            pass
    return start(bot)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
