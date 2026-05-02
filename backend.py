from flask import Flask, render_template, request, redirect, url_for, session, jsonify
import random
import os

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-me")

# DATABASE 
players = {}   # id -> {name, role}
game_started = False


@app.route("/", methods=["GET", "POST"])
def index():
    global players

    if request.method == "POST":
        name = request.form["name"]
        
        if name:
            player_id = str(len(players))
            players[player_id] = {"name": name, "role": None}

            session["player_id"] = player_id

        return redirect(url_for("wait"))

    return render_template("index.html")


# =========================
@app.route("/wait")
def wait():
    pid = session.get("player_id")
    is_host = False
    if pid and pid in players:
        if players[pid]["name"] == "faracha":
            is_host = True

    return render_template("wait.html", players=players, started=game_started, is_host=is_host)

# ========================= 
@app.route("/host", methods=["GET", "POST"])
def host():
    global game_started

    if request.method == "POST":
        mafia = int(request.form["mafia"])
        doctor = int(request.form["doctor"])
        n9awad = int(request.form["n9awad"])
        w9 = int(request.form["w9"])
        taskit = int(request.form["mafia taskit"])
        ghamir = int(request.form["ghamir aw ghadir"])
        haway = int(request.form["mafia haway"])

        roles = (
            ["mafia"] * mafia +
            ["tbib"] * doctor +
            ["saiad"] * w9 + 
            ["mafia taskit"] * taskit +
            ["ghamir aw ghadir"] * ghamir + 
            ["9awad"] * n9awad +
            ["mafia haway"] * haway

        )

        remaining = len(players) - len(roles)
        roles += ["good citizen"] * remaining

        for i in range(random.randint(5,20)):
            random.shuffle(roles)

        i = 0
        for pid in players:
            players[pid]["role"] = roles[i]
            i += 1

        game_started = True

        return redirect(url_for("wait"))

    return render_template("host.html", players=players)


# =========================
@app.route("/role")
def role():
    if not game_started:
        return redirect(url_for("wait"))

    pid = session.get("player_id")

    if not pid or pid not in players:
        return redirect(url_for("index"))
    
    player = players[pid]

    pid = session.get("player_id")
    is_host = False
    if pid and pid in players:
        if players[pid]["name"] == "faracha":
            is_host = True
    return render_template("role.html", player=player,is_host=is_host)

@app.route("/data")
def data():
    return jsonify({
        "players": [p["name"] for p in players.values()],
        "started": game_started
    })

# =========================
# RESET
@app.route("/reset")
def reset():
    global players, game_started
    players = {}
    game_started = False
    session.clear()
    return redirect(url_for("index"))


# =========================
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)