# app.py
# Main Flask file for the encryption project.
# Handles the pages, the form, file upload, the database and login.

import os
import io
import time
import sqlite3
from datetime import datetime

from flask import Flask, render_template, request, redirect, url_for, send_file, flash
from flask_login import LoginManager, UserMixin, login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

import encryption


# folders and database file
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOAD_FOLDER = os.path.join(BASE_DIR, "uploads")
DB_PATH = os.path.join(BASE_DIR, "history.db")

if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

app = Flask(__name__)
app.secret_key = "my-secret-key-123"
app.config["UPLOAD_FOLDER"] = UPLOAD_FOLDER


# ---------- Login setup ----------
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"


class User(UserMixin):
    def __init__(self, id, username, password_hash):
        self.id = id
        self.username = username
        self.password_hash = password_hash


@login_manager.user_loader
def load_user(user_id):
    row = run_query("SELECT * FROM users WHERE id = ?", (user_id,), one=True)
    if row:
        return User(row["id"], row["username"], row["password_hash"])
    return None


# ---------- Database helpers ----------
def get_db():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def run_query(query, args=(), one=False):
    conn = get_db()
    cur = conn.execute(query, args)
    rows = cur.fetchall()
    conn.commit()
    conn.close()
    if one:
        if rows:
            return rows[0]
        return None
    return rows


def init_db():
    conn = get_db()
    conn.execute("""CREATE TABLE IF NOT EXISTS users (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        username TEXT UNIQUE NOT NULL,
                        password_hash TEXT NOT NULL)""")
    conn.execute("""CREATE TABLE IF NOT EXISTS history (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        algorithm TEXT,
                        original TEXT,
                        encrypted TEXT,
                        decrypted TEXT,
                        key TEXT,
                        enc_time_ms REAL,
                        dec_time_ms REAL,
                        created_at TEXT)""")
    conn.commit()
    conn.close()


# ---------- Pages ----------
@app.route("/")
def index():
    return render_template("index.html", algorithms=encryption.ALGORITHMS)


@app.route("/encrypt", methods=["POST"])
def encrypt():
    algorithm = request.form.get("algorithm", "caesar")
    key = request.form.get("key", "").strip()
    text = request.form.get("text", "")

    # if the user uploaded a .txt file, use its content
    file = request.files.get("file")
    if file and file.filename != "":
        if not file.filename.lower().endswith(".txt"):
            flash("Only .txt files are allowed.")
            return redirect(url_for("index"))
        filename = secure_filename(file.filename)
        path = os.path.join(app.config["UPLOAD_FOLDER"], filename)
        file.save(path)
        f = open(path, "r", encoding="utf-8", errors="replace")
        text = f.read()
        f.close()

    # simple checks on the input
    if text == "":
        flash("Please type some text or upload a file.")
        return redirect(url_for("index"))
    if key == "" or not is_integer(key):
        flash("The key must be a whole number.")
        return redirect(url_for("index"))
    if algorithm not in encryption.ALGORITHMS:
        flash("Please choose an algorithm.")
        return redirect(url_for("index"))

    # encrypt and measure the time (bonus 3)
    start = time.perf_counter()
    if algorithm == "caesar":
        encrypted, enc_steps = encryption.caesar_encrypt(text, key)
    elif algorithm == "xor":
        encrypted, enc_steps = encryption.xor_encrypt(text, key)
    else:
        encrypted, enc_steps = encryption.mrc_encrypt(text, key)
    enc_time = (time.perf_counter() - start) * 1000

    # decrypt and measure the time
    start = time.perf_counter()
    if algorithm == "caesar":
        decrypted, dec_steps = encryption.caesar_decrypt(encrypted, key)
    elif algorithm == "xor":
        decrypted, dec_steps = encryption.xor_decrypt(encrypted, key)
    else:
        decrypted, dec_steps = encryption.mrc_decrypt(encrypted, key)
    dec_time = (time.perf_counter() - start) * 1000

    result = {
        "original": text,
        "algorithm_name": encryption.ALGORITHMS[algorithm],
        "encrypted": encrypted,
        "encryption_steps": enc_steps,
        "decrypted": decrypted,
        "decryption_steps": dec_steps,
        "key": key,
        "enc_time": round(enc_time, 4),
        "dec_time": round(dec_time, 4),
    }

    # save to the history table (bonus 2)
    if current_user.is_authenticated:
        user_id = current_user.id
    else:
        user_id = None
    run_query("""INSERT INTO history
                 (user_id, algorithm, original, encrypted, decrypted, key, enc_time_ms, dec_time_ms, created_at)
                 VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
              (user_id, result["algorithm_name"], text, encrypted, decrypted, str(key),
               result["enc_time"], result["dec_time"], datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

    return render_template("result.html", r=result)


# bonus 1 - download the result as a .txt file
@app.route("/download", methods=["POST"])
def download():
    content = request.form.get("content", "")
    kind = request.form.get("kind", "output")
    buffer = io.BytesIO(content.encode("utf-8"))
    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=kind + ".txt", mimetype="text/plain")


# bonus 2 and 4 - history table and performance chart
@app.route("/history")
def history():
    if current_user.is_authenticated:
        rows = run_query("SELECT * FROM history WHERE user_id = ? ORDER BY id DESC", (current_user.id,))
    else:
        rows = run_query("SELECT * FROM history WHERE user_id IS NULL ORDER BY id DESC")

    # work out the average time for each algorithm for the chart
    chart = {}
    for name in encryption.ALGORITHMS.values():
        enc_list = []
        dec_list = []
        for row in rows:
            if row["algorithm"] == name:
                if row["enc_time_ms"] is not None:
                    enc_list.append(row["enc_time_ms"])
                if row["dec_time_ms"] is not None:
                    dec_list.append(row["dec_time_ms"])
        if len(enc_list) > 0:
            avg_enc = round(sum(enc_list) / len(enc_list), 4)
        else:
            avg_enc = 0
        if len(dec_list) > 0:
            avg_dec = round(sum(dec_list) / len(dec_list), 4)
        else:
            avg_dec = 0
        chart[name] = {"enc": avg_enc, "dec": avg_dec}

    return render_template("history.html", rows=rows, chart=chart)


# bonus 5 - register, login, logout
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        confirm = request.form.get("confirm", "")

        # validation checks
        if username == "" or password == "":
            flash("Please fill in all the fields.")
            return redirect(url_for("register"))
        if len(username) < 3:
            flash("Username must be at least 3 characters.")
            return redirect(url_for("register"))
        if not username.replace("_", "").isalnum():
            flash("Username can only use letters, numbers and underscore.")
            return redirect(url_for("register"))
        if len(password) < 6:
            flash("Password must be at least 6 characters.")
            return redirect(url_for("register"))
        if password != confirm:
            flash("The two passwords do not match.")
            return redirect(url_for("register"))

        # make sure the username is not taken
        existing = run_query("SELECT * FROM users WHERE username = ?", (username,), one=True)
        if existing:
            flash("That username already exists.")
            return redirect(url_for("register"))

        run_query("INSERT INTO users (username, password_hash) VALUES (?, ?)",
                  (username, generate_password_hash(password)))
        flash("Account created. You can log in now.")
        return redirect(url_for("login"))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        row = run_query("SELECT * FROM users WHERE username = ?", (username,), one=True)
        if row and check_password_hash(row["password_hash"], password):
            user = User(row["id"], row["username"], row["password_hash"])
            login_user(user)
            flash("Welcome, " + username + "!")
            return redirect(url_for("index"))
        flash("Wrong username or password.")
        return redirect(url_for("login"))
    return render_template("login.html")


@app.route("/logout")
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for("index"))


# checks if a string is a whole number (works for negatives too)
def is_integer(value):
    try:
        int(value)
        return True
    except ValueError:
        return False


if __name__ == "__main__":
    init_db()
    app.run(debug=True)
