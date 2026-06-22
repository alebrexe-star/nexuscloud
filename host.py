from flask import Flask, request, redirect
import os, zipfile, subprocess

app = Flask(__name__)

BOTS = "bots"
UPLOADS = "uploads"

os.makedirs(BOTS, exist_ok=True)
os.makedirs(UPLOADS, exist_ok=True)

processos = {}

def find_bot(path):
    if os.path.exists(os.path.join(path, "main.py")):
        return "main.py"
    if os.path.exists(os.path.join(path, "bot.py")):
        return "bot.py"
    return None

@app.route("/")
def home():
    bots = os.listdir(BOTS)

    html = "<h1>Nexuscloud SaaS</h1>"
    html += "<h2>Upload Bot</h2>"
    html += '''
    <form action="/upload" method="post" enctype="multipart/form-data">
        <input type="file" name="file">
        <button>Enviar</button>
    </form>
    <hr>
    <h2>Bots</h2>
    '''

    for bot in bots:
        html += f"""
        <p>
        🤖 {bot}
        <a href="/start/{bot}">Start</a>
        <a href="/restart/{bot}">Restart</a>
        </p>
        """

    return html

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
    file = find_bot(path)

    if not file:
        return "bot.py ou main.py não encontrado"

    full = os.path.join(path, file)

    log = open(os.path.join(path, "log.txt"), "w")

    p = subprocess.Popen(
        ["python", full],
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
