import json
import os
import random
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, session, url_for

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-secret-key-for-production")

LEADERBOARD_FILE = os.path.join(app.root_path, "leaderboard.json")

DIFFICULTIES = {
    "easy": {"label": "Easy", "max_number": 50, "attempts": 7},
    "medium": {"label": "Medium", "max_number": 100, "attempts": 5},
    "hard": {"label": "Hard", "max_number": 200, "attempts": 3},
}


def load_leaderboard():
    """Read saved scores. Return an empty list if the file is missing or invalid."""
    if not os.path.exists(LEADERBOARD_FILE):
        return []

    try:
        with open(LEADERBOARD_FILE, "r", encoding="utf-8") as file:
            data = json.load(file)
        return data if isinstance(data, list) else []
    except (json.JSONDecodeError, OSError):
        return []


def save_leaderboard_record():
    """Save this completed game session once."""
    if session.get("record_saved"):
        return

    players = load_leaderboard()
    players.append({
        "username": session.get("username", "Player"),
        "score": session.get("score", 0),
        "wins": session.get("wins", 0),
        "losses": session.get("losses", 0),
        "total_rounds": session.get("total_rounds", 0),
        "date": datetime.now().strftime("%d-%m-%Y %H:%M"),
    })
    players.sort(
        key=lambda player: (player.get("score", 0), player.get("wins", 0)),
        reverse=True,
    )

    try:
        with open(LEADERBOARD_FILE, "w", encoding="utf-8") as file:
            json.dump(players, file, indent=4)
        session["record_saved"] = True
    except OSError:
        flash("Score save nahi ho paya. Please try again.", "error")


def begin_round(difficulty_key):
    settings = DIFFICULTIES[difficulty_key]
    session["difficulty"] = difficulty_key
    session["max_number"] = settings["max_number"]
    session["max_attempts"] = settings["attempts"]
    session["attempts_left"] = settings["attempts"]
    session["secret_number"] = random.randint(1, settings["max_number"])
    session["round_over"] = False
    session["feedback"] = "Secret number guess karo. Good luck!"
    session["feedback_type"] = "info"


@app.route("/")
def home():
    return render_template("index.html", difficulties=DIFFICULTIES)


@app.route("/start", methods=["POST"])
def start_game():
    username = request.form.get("username", "").strip()
    difficulty = request.form.get("difficulty", "easy").lower()

    if not username:
        flash("Please apna username enter karo.", "error")
        return redirect(url_for("home"))

    if difficulty not in DIFFICULTIES:
        flash("Please valid difficulty select karo.", "error")
        return redirect(url_for("home"))

    session.clear()
    session.update({
        "username": username[:24],
        "score": 0,
        "wins": 0,
        "losses": 0,
        "total_rounds": 0,
        "record_saved": False,
    })
    begin_round(difficulty)
    return redirect(url_for("game"))


@app.route("/game")
def game():
    if "secret_number" not in session:
        return redirect(url_for("home"))

    difficulty = DIFFICULTIES[session["difficulty"]]
    return render_template(
        "game.html",
        username=session.get("username", "Player"),
        difficulty=difficulty,
        score=session.get("score", 0),
        wins=session.get("wins", 0),
        losses=session.get("losses", 0),
        total_rounds=session.get("total_rounds", 0),
        attempts_left=session.get("attempts_left", 0),
        max_number=session.get("max_number", 50),
        feedback=session.get("feedback", ""),
        feedback_type=session.get("feedback_type", "info"),
        round_over=session.get("round_over", False),
        session_difficulty=session.get("difficulty", "easy"),
    )


@app.route("/guess", methods=["POST"])
def submit_guess():
    if "secret_number" not in session:
        return redirect(url_for("home"))

    if session.get("round_over"):
        return redirect(url_for("game"))

    raw_guess = request.form.get("guess", "").strip()
    try:
        guess = int(raw_guess)
    except (TypeError, ValueError):
        session["feedback"] = "Valid whole number enter karo."
        session["feedback_type"] = "error"
        return redirect(url_for("game"))

    max_number = session["max_number"]
    if guess < 1 or guess > max_number:
        session["feedback"] = f"Number 1 se {max_number} ke beech hona chahiye."
        session["feedback_type"] = "error"
        return redirect(url_for("game"))

    session["attempts_left"] -= 1
    secret = session["secret_number"]

    if guess == secret:
        session["feedback"] = f"Awesome! {secret} bilkul correct hai. Tumne round jeet liya!"
        session["feedback_type"] = "success"
        session["score"] += 10
        session["wins"] += 1
        session["total_rounds"] += 1
        session["round_over"] = True
    elif session["attempts_left"] <= 0:
        session["feedback"] = f"Attempts khatam! Secret number {secret} tha. Next round mein try karna."
        session["feedback_type"] = "error"
        session["losses"] += 1
        session["total_rounds"] += 1
        session["round_over"] = True
    elif guess > secret:
        session["feedback"] = "Too High! Thoda chhota number try karo."
        session["feedback_type"] = "warning"
    else:
        session["feedback"] = "Too Low! Thoda bada number try karo."
        session["feedback_type"] = "warning"

    return redirect(url_for("game"))


@app.route("/next-round", methods=["POST"])
def next_round():
    if "username" not in session:
        return redirect(url_for("home"))
    if not session.get("round_over"):
        return redirect(url_for("game"))

    difficulty = request.form.get("difficulty", session.get("difficulty", "easy"))
    if difficulty not in DIFFICULTIES:
        difficulty = session.get("difficulty", "easy")
    begin_round(difficulty)
    return redirect(url_for("game"))


@app.route("/finish", methods=["POST"])
def finish_game():
    if "username" in session:
        save_leaderboard_record()
    summary = {
        "username": session.get("username", "Player"),
        "score": session.get("score", 0),
        "wins": session.get("wins", 0),
        "losses": session.get("losses", 0),
        "total_rounds": session.get("total_rounds", 0),
    }
    session.clear()
    return render_template("result.html", summary=summary)


@app.route("/leaderboard")
def leaderboard():
    players = load_leaderboard()
    players.sort(
        key=lambda player: (player.get("score", 0), player.get("wins", 0)),
        reverse=True,
    )
    return render_template("leaderboard.html", players=players[:10])


if __name__ == "__main__":
    app.run(debug=True)
