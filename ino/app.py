from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.security import check_password_hash
import socket

# --- CONFIGURACIÓN DE AUTENTICACIÓN (cambia estos valores) ---
APP_USER = "admin"   # Usuario
APP_PW_HASH = "scrypt:32768:8:1$Z2Z2sdfSDf...$..."   # Reemplaza con hash real de tu contraseña
SECRET_KEY = "clave-secreta-muy-larga-y-aleatoria"
# ------------------------------------------------------------

TCP_HOST = "127.0.0.1"
TCP_PORT = 5001

app = Flask(__name__)
app.secret_key = SECRET_KEY

def is_logged_in():
    return session.get("logged_in") is True

def send_cmd(cmd: str) -> str:
    """Envía un comando TCP y devuelve la respuesta."""
    try:
        with socket.create_connection((TCP_HOST, TCP_PORT), timeout=2) as s:
            s.sendall((cmd + "\n").encode("utf-8"))
            return s.recv(1024).decode("utf-8", errors="ignore").strip()
    except Exception as e:
        return f"ERR:{str(e)}"

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = request.form.get("username", "").strip()
        pw = request.form.get("password", "")
        if user == APP_USER and check_password_hash(APP_PW_HASH, pw):
            session["logged_in"] = True
            return redirect(url_for("index"))
        return render_template("login.html", error="Usuario o contraseña incorrectos")
    return render_template("login.html", error=None)

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

@app.route("/")
def index():
    if not is_logged_in():
        return redirect(url_for("login"))
    return render_template("index.html")

@app.get("/api/estado")
def get_estado():
    """Devuelve los últimos valores del sensor de temperatura."""
    if not is_logged_in():
        return jsonify({"ok": False, "error": "No autorizado"}), 401

    resp = send_cmd("GET_STATE")
    # Se espera "TEMP:25.5,ZONA:2,VEL:170"
    try:
        partes = resp.split(",")
        temp = float(partes[0].split(":")[1])
        zona = int(partes[1].split(":")[1])
        velocidad = int(partes[2].split(":")[1])
        return jsonify({
            "ok": True,
            "temperatura": temp,
            "zona": zona,
            "velocidad": velocidad
        })
    except Exception as e:
        return jsonify({"ok": False, "error": f"Respuesta inválida: {resp}"})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
