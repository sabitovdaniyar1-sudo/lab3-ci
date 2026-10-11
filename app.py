from flask import Flask, request, jsonify, render_template, redirect, url_for
import os
import sqlite3

app = Flask(__name__)
# ИСПРАВЛЕНО: путь к БД берётся из переменной окружения (в Docker это общий том /data)
DB = os.environ.get("USERS_DB", "users.db")


def init_db():
    folder = os.path.dirname(DB)
    if folder:
        os.makedirs(folder, exist_ok=True)
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            email TEXT NOT NULL UNIQUE
        )
    """)
    conn.commit()
    conn.close()


@app.route("/")
def index():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    users = cursor.fetchall()
    conn.close()
    return render_template("index.html", users=users)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        conn = sqlite3.connect(DB)
        cursor = conn.cursor()
        # ИСПРАВЛЕНО: при дубликате соединение закрывается (иначе "database is locked")
        try:
            cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (name, email))
            conn.commit()
        except sqlite3.IntegrityError:
            conn.rollback()
            conn.close()
            return "Email already exists", 400
        conn.close()
        return redirect(url_for("index"))
    return render_template("register.html")


# API
@app.route("/api/users", methods=["GET"])
def api_get_users():
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("SELECT id, name, email FROM users")
    users = cursor.fetchall()
    conn.close()
    return jsonify([{"id": u[0], "name": u[1], "email": u[2]} for u in users])


@app.route("/api/users", methods=["POST"])
def api_create_user():
    data = request.json
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    # ИСПРАВЛЕНО: при дубликате соединение закрывается, API возвращает 400
    try:
        cursor.execute("INSERT INTO users (name, email) VALUES (?, ?)", (data["name"], data["email"]))
        conn.commit()
    except sqlite3.IntegrityError:
        conn.rollback()
        conn.close()
        return jsonify({"error": "email already exists"}), 400
    user_id = cursor.lastrowid
    conn.close()
    return jsonify({"id": user_id, "name": data["name"], "email": data["email"]}), 201


@app.route("/api/users/<int:user_id>", methods=["DELETE"])
def api_delete_user(user_id):
    conn = sqlite3.connect(DB)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM users WHERE id = ?", (user_id,))
    conn.commit()
    conn.close()
    return "", 204


if __name__ == "__main__":
    init_db()
    # ИСПРАВЛЕНО: host="0.0.0.0" - иначе приложение недоступно снаружи контейнера;
    # debug по умолчанию выключен
    app.run(host="0.0.0.0", port=5000, debug=os.environ.get("FLASK_DEBUG", "0") == "1")
