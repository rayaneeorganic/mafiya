from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
import os
import string

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

rooms = {}


def generate_room_code():
    while True:
        code = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
        if code not in rooms:
            return code


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/create", methods=["GET", "POST"])
def create():
    if request.method == "POST":
        name = request.form["name"].strip()
        password = request.form["password"].strip()

        if not name or not password:
            return render_template("create.html", error="Name and password are required.")

        room_code = generate_room_code()
        admin_id = "0"

        rooms[room_code] = {
            "password": password,
            "players": {admin_id: {"name": name, "role": None}},
            "game_started": False,
            "admin_id": admin_id,
        }

        session["room_code"] = room_code
        session["player_id"] = admin_id

        return redirect(url_for("wait"))

    return render_template("create.html", error=None)


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
            return render_template("join.html", error="Game already started, you can't join now.")

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
    pid = session.get("player_id")

    if not room_code or room_code not in rooms:
        return redirect(url_for("index"))

    room = rooms[room_code]
    is_host = pid == room["admin_id"]

    return render_template(
        "wait.html",
        players=room["players"],
        started=room["game_started"],
        is_host=is_host,
        room_code=room_code,
    )


@app.route("/host", methods=["GET", "POST"])
def host():
    room_code = session.get("room_code")
    pid = session.get("player_id")

    if not room_code or room_code not in rooms:
        return redirect(url_for("index"))

    room = rooms[room_code]

    if pid != room["admin_id"]:
        return redirect(url_for("wait"))

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

        for i, p_id in enumerate(room["players"]):
            room["players"][p_id]["role"] = roles[i]

        room["game_started"] = True

        return redirect(url_for("wait"))

    return render_template("host.html", players=room["players"])


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
    is_host = pid == room["admin_id"]

    return render_template("role.html", player=player, is_host=is_host)


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


@app.route("/reset")
def reset():
    room_code = session.get("room_code")
    pid = session.get("player_id")

    if room_code and room_code in rooms:
        if pid == rooms[room_code]["admin_id"]:
            del rooms[room_code]

    session.clear()
    return redirect(url_for("index"))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
