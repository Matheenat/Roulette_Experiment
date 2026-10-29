import os
import sqlite3
import uuid
from datetime import timedelta

from flask import Flask, jsonify, render_template, request, session

import storage
from config import (BET_CHIPS, CORRECT_ODDS_OPTION, ODDS_OPTIONS,
                    ODDS_QUESTION, START_BALANCE)
from game import Color, play_round

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-only-change-me")
if "SECRET_KEY" not in os.environ:
    app.logger.warning("SECRET_KEY is not set: using an insecure development key.")
app.permanent_session_lifetime = timedelta(days=1)
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("COOKIE_SECURE") == "1",
)

storage.init_db()

def error(message, status=400):
    return jsonify({"error": message}), status

def current_session():
    return storage.get_session(session.get("session_id"))

def balance_of(s, rounds):
    return rounds[-1]["balance_after"] if rounds else s["start_balance"]

def clean_seconds(value):
    """Decision time comes from the browser, so only accept sane numbers."""
    if (isinstance(value, (int, float)) and not isinstance(value, bool)
            and 0 <= value <= 3600):
        return round(float(value), 2)
    return None

def build_summary(s, rounds):
    wagered = sum(r["bet_amount"] for r in rounds)
    final_balance = balance_of(s, rounds)
    return {
        "rounds": len(rounds),
        "wins": sum(r["win"] for r in rounds),
        "wagered": wagered,
        "final_balance": final_balance,
        "net": final_balance - s["start_balance"],
        "expected_loss": round(wagered / 37),   # house edge: 1/37 of all money wagered
        "odds_before": s["odds_before"],
        "odds_after": s["odds_after"],
        "correct_option": CORRECT_ODDS_OPTION,
    }

def state_payload(s):
    if s is None:
        return {"stage": "consent", "balance": START_BALANCE, "rounds": []}
    rounds = storage.get_rounds(s["session_id"])
    return {
        "stage": s["stage"],
        "balance": balance_of(s, rounds),
        "rounds": rounds,
        "summary": build_summary(s, rounds) if s["stage"] == "reveal" else None,
    }

@app.route("/")
def index():
    return render_template(
        "index.html",
        chips=BET_CHIPS,
        odds_question=ODDS_QUESTION,
        odds_options=ODDS_OPTIONS,
        start_balance=START_BALANCE,
    )

@app.get("/api/state")
def get_state():
    return jsonify(state_payload(current_session()))

@app.post("/api/start")
def start():
    data = request.get_json(silent=True) or {}
    if data.get("consent") is not True:
        return error("Consent is required.")
    if data.get("odds_before") not in ODDS_OPTIONS:
        return error("Please choose one of the answers.")
    if current_session():
        return error("A session is already in progress.", 409)

    sid = str(uuid.uuid4())
    storage.create_session(sid, data["odds_before"], START_BALANCE)
    session.permanent = True
    session["session_id"] = sid
    return jsonify(state_payload(storage.get_session(sid)))

@app.post("/api/spin")
def spin_route():
    s = current_session()
    if not s or s["stage"] != "game":
        return error("No game in progress.", 409)

    data = request.get_json(silent=True) or {}
    bet = data.get("bet")
    bet_type = data.get("bet_type")
    if not isinstance(bet, int) or isinstance(bet, bool):
        return error("Bet must be a whole number.")
    try:
        Color(bet_type)
    except ValueError:
        return error("Choose red, black or green.")

    rounds = storage.get_rounds(s["session_id"])
    try:
        result = play_round(bet_type, bet, balance_of(s, rounds))
    except ValueError as e:
        return error(str(e))

    result["round_no"] = len(rounds) + 1
    result["decision_seconds"] = clean_seconds(data.get("decision_seconds"))
    result["timestamp"] = storage.now()
    try:
        storage.save_round(s["session_id"], result)
    except sqlite3.IntegrityError:        # double submit of the same round
        return error("That round was already played.", 409)

    stage = "game"
    if result["balance_after"] == 0:
        storage.end_play(s["session_id"], "bust")
        stage = "post"
    return jsonify({"round": result, "balance": result["balance_after"],
                    "stage": stage})

@app.post("/api/stop")
def stop():
    s = current_session()
    if not s or s["stage"] != "game":
        return error("No game in progress.", 409)
    if not storage.get_rounds(s["session_id"]):
        return error("Play at least one round first.", 409)
    storage.end_play(s["session_id"], "stopped")
    return jsonify(state_payload(storage.get_session(s["session_id"])))

@app.post("/api/finish")
def finish():
    s = current_session()
    if not s or s["stage"] != "post":
        return error("Not ready for the final question.", 409)
    data = request.get_json(silent=True) or {}
    if data.get("odds_after") not in ODDS_OPTIONS:
        return error("Please choose one of the answers.")
    storage.finish_session(s["session_id"], data["odds_after"])
    return jsonify(state_payload(storage.get_session(s["session_id"])))

@app.post("/api/history-view")
def history_view():
    s = current_session()
    if not s or s["stage"] not in ("game", "post"):
        return error("No game in progress.", 409)
    storage.add_history_view(s["session_id"])
    return jsonify({"ok": True})

if __name__ == "__main__":
    app.run(debug=True)