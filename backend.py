from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
import os
import string

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "faracha")

rooms = {}


def generate_room_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in rooms:
            return code


# ── Player routes ──────────────────────────────────────────────

@app.route("/")
def index():
    return render_template("index.html")


@app.route("/join", methods=["GET", "POST"])
def join():
    if request.method == "POST":
        name = request.form["name"].strip()
        room_code = request.form["room_code"].strip().upper()
        password = request.form["password"].strip()

        if room_code not in rooms:
            return render_template("join.html", error="Room not found.")
        room = rooms[room_code]
        if room["password"] != password:
            return render_template("join.html", error="Wrong password.")
        if room["game_started"]:
            return render_template("join.html", error="Game already started, can't join now.")
        if not name:
            return render_template("join.html", error="Enter your name.")

        player_id = str(len(room["players"]))
        room["players"][player_id] = {"name": name, "role": None}
        session["room_code"] = room_code
        session["player_id"] = player_id

        return redirect(url_for("wait"))

    return render_template("join.html", error=None)


@app.route("/wait")
def wait():
    room_code = session.get("room_code")
    if not room_code or room_code not in rooms:
        return redirect(url_for("index"))
    room = rooms[room_code]
    return render_template("wait.html", players=room["players"], started=room["game_started"], room_code=room_code)


@app.route("/role")
def role():
    room_code = session.get("room_code")
    pid = session.get("player_id")
    if not room_code or room_code not in rooms:
        return redirect(url_for("index"))
    room = rooms[room_code]
    if not room["game_started"]:
        return redirect(url_for("wait"))
    if not pid or pid not in room["players"]:
        return redirect(url_for("index"))
    player = room["players"][pid]
    return render_template("role.html", player=player, is_host=False)


@app.route("/data")
def data():
    room_code = session.get("room_code")
    if not room_code or room_code not in rooms:
        return jsonify({"players": [], "started": False})
    room = rooms[room_code]
    return jsonify({
        "players": [p["name"] for p in room["players"].values()],
        "started": room["game_started"],
    })


# ── Admin routes ───────────────────────────────────────────────

def admin_logged_in():
    return session.get("is_admin") is True


@app.route("/admin", methods=["GET", "POST"])
def admin_login():
    if admin_logged_in():
        return redirect(url_for("admin_dashboard"))

    error = None
    if request.method == "POST":
        if request.form["password"] == ADMIN_PASSWORD:
            session["is_admin"] = True
            return redirect(url_for("admin_dashboard"))
        error = "Wrong password."

    return render_template("admin_login.html", error=error)


@app.route("/admin/dashboard")
def admin_dashboard():
    if not admin_logged_in():
        return redirect(url_for("admin_login"))
    return render_template("admin_dashboard.html", rooms=rooms)


@app.route("/admin/create", methods=["POST"])
def admin_create_room():
    if not admin_logged_in():
        return redirect(url_for("admin_login"))

    password = request.form["password"].strip()
    if not password:
        return redirect(url_for("admin_dashboard"))

    room_code = generate_room_code()
    rooms[room_code] = {
        "password": password,
        "players": {},
        "game_started": False,
    }
    return redirect(url_for("admin_host", room_code=room_code))


@app.route("/admin/room/<room_code>", methods=["GET", "POST"])
def admin_host(room_code):
    if not admin_logged_in():
        return redirect(url_for("admin_login"))
    if room_code not in rooms:
        return redirect(url_for("admin_dashboard"))

    room = rooms[room_code]

    if request.method == "POST":
        mafia = int(request.form["mafia"])
        doctor = int(request.form["doctor"])
        n9awad = int(request.form["n9awad"])
        w9 = int(request.form["w9"])
        taskit = int(request.form["mafia_taskit"])
        ghamir = int(request.form["ghamir_aw_ghadir"])
        haway = int(request.form["mafia_haway"])

        roles = (
            ["mafia"] * mafia
            + ["tbib"] * doctor
            + ["saiad"] * w9
            + ["mafia taskit"] * taskit
            + ["ghamir aw ghadir"] * ghamir
            + ["9awad"] * n9awad
            + ["mafia haway"] * haway
        )

        remaining = len(room["players"]) - len(roles)
        roles += ["good citizen"] * remaining

        for _ in range(random.randint(5, 20)):
            random.shuffle(roles)

        for i, pid in enumerate(room["players"]):
            room["players"][pid]["role"] = roles[i]

        room["game_started"] = True
        return redirect(url_for("admin_host", room_code=room_code))

    return render_template("admin_host.html", room=room, room_code=room_code)


@app.route("/admin/room/<room_code>/reset")
def admin_reset_room(room_code):
    if not admin_logged_in():
        return redirect(url_for("admin_login"))
    if room_code in rooms:
        del rooms[room_code]
    return redirect(url_for("admin_dashboard"))


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    return redirect(url_for("admin_login"))


# ── Run ────────────────────────────────────────────────────────

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
