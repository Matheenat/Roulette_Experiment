import os
import sqlite3
import tempfile

# Use a throwaway database; this must be set before app.py is imported.
os.environ["DB_PATH"] = os.path.join(tempfile.mkdtemp(), "import.db")

import pytest
import game
import storage
from app import app
from config import CORRECT_ODDS_OPTION, ODDS_OPTIONS

@pytest.fixture
def client(tmp_path, monkeypatch):
    monkeypatch.setattr(storage, "DB_PATH", str(tmp_path / "test.db"))
    storage.init_db()
    app.config["TESTING"] = True
    return app.test_client()

def start(client, answer=ODDS_OPTIONS[1]):
    return client.post("/api/start", json={"consent": True, "odds_before": answer})

def force_pocket(monkeypatch, pocket):
    monkeypatch.setattr(game, "spin", lambda: pocket)

def test_state_before_start_is_consent(client):
    data = client.get("/api/state").get_json()
    assert data["stage"] == "consent"
    assert data["balance"] == game.START_BALANCE

def test_spin_without_session_is_rejected(client):
    r = client.post("/api/spin", json={"bet": 10, "bet_type": "red"})
    assert r.status_code == 409

def test_start_needs_consent_and_a_valid_answer(client):
    assert client.post("/api/start", json={"consent": False,
                                           "odds_before": ODDS_OPTIONS[0]}).status_code == 400
    assert client.post("/api/start", json={"consent": True,
                                           "odds_before": "banana"}).status_code == 400
    assert client.get("/api/state").get_json()["stage"] == "consent"

def test_cannot_start_twice(client):
    assert start(client).status_code == 200
    assert start(client).status_code == 409

def test_win_updates_balance_and_is_saved(client, monkeypatch):
    start(client)
    force_pocket(monkeypatch, 3)                       # red
    r = client.post("/api/spin", json={"bet": 20, "bet_type": "red",
                                       "decision_seconds": 1.5})
    body = r.get_json()
    assert r.status_code == 200
    assert body["round"]["win"] == 1
    assert body["balance"] == 1020
    assert body["stage"] == "game"

    state = client.get("/api/state").get_json()      # same cookie = resume
    assert state["balance"] == 1020
    assert len(state["rounds"]) == 1
    assert state["rounds"][0]["round_no"] == 1
    assert state["rounds"][0]["decision_seconds"] == 1.5

def test_invalid_spins_are_rejected(client):
    start(client)
    assert client.post("/api/spin", json={"bet": 5000, "bet_type": "red"}).status_code == 400
    assert client.post("/api/spin", json={"bet": 0, "bet_type": "red"}).status_code == 400
    assert client.post("/api/spin", json={"bet": 10, "bet_type": "Red"}).status_code == 400
    assert client.post("/api/spin", json={"bet": "10", "bet_type": "red"}).status_code == 400
    assert client.post("/api/spin", json={"bet": True, "bet_type": "red"}).status_code == 400
    assert client.get("/api/state").get_json()["rounds"] == []

def test_bad_decision_seconds_are_stored_as_null(client, monkeypatch):
    start(client)
    force_pocket(monkeypatch, 3)
    client.post("/api/spin", json={"bet": 10, "bet_type": "red",
                                   "decision_seconds": -5})
    assert client.get("/api/state").get_json()["rounds"][0]["decision_seconds"] is None

def test_going_bust_moves_to_the_final_question(client, monkeypatch):
    start(client)
    force_pocket(monkeypatch, 3)                       # red, so black loses
    r = client.post("/api/spin", json={"bet": 1000, "bet_type": "black"})
    body = r.get_json()
    assert body["balance"] == 0
    assert body["stage"] == "post"
    assert client.get("/api/state").get_json()["stage"] == "post"
    # no more spins once the game is over
    assert client.post("/api/spin", json={"bet": 10, "bet_type": "red"}).status_code == 409

def test_stop_needs_at_least_one_round(client):
    start(client)
    assert client.post("/api/stop", json={}).status_code == 409

def test_full_session_flow_and_summary(client, monkeypatch):
    start(client, ODDS_OPTIONS[1])
    force_pocket(monkeypatch, 3)                       # red
    client.post("/api/spin", json={"bet": 20, "bet_type": "red"})      # +20
    client.post("/api/spin", json={"bet": 50, "bet_type": "black"})    # -50
    client.post("/api/history-view", json={})

    assert client.post("/api/finish", json={"odds_after": ODDS_OPTIONS[2]}).status_code == 409
    assert client.post("/api/stop", json={}).get_json()["stage"] == "post"

    assert client.post("/api/finish", json={"odds_after": "banana"}).status_code == 400
    r = client.post("/api/finish", json={"odds_after": ODDS_OPTIONS[2]})
    summary = r.get_json()["summary"]

    assert r.get_json()["stage"] == "reveal"
    assert summary["rounds"] == 2
    assert summary["wins"] == 1
    assert summary["wagered"] == 70
    assert summary["final_balance"] == 970
    assert summary["net"] == -30
    assert summary["expected_loss"] == 2              # 70 / 37, rounded
    assert summary["odds_before"] == ODDS_OPTIONS[1]
    assert summary["odds_after"] == ODDS_OPTIONS[2]
    assert summary["correct_option"] == CORRECT_ODDS_OPTION

    row = storage.get_session(_only_session_id())
    assert row["ended_by"] == "stopped"
    assert row["history_views"] == 1
    assert row["ended_at"] is not None

def test_same_round_cannot_be_saved_twice(client, monkeypatch):
    start(client)
    force_pocket(monkeypatch, 3)
    client.post("/api/spin", json={"bet": 10, "bet_type": "red"})
    sid = _only_session_id()
    duplicate = dict(storage.get_rounds(sid)[0])
    with pytest.raises(sqlite3.IntegrityError):
        storage.save_round(sid, duplicate)

def _only_session_id():
    with storage.db() as conn:
        return conn.execute("SELECT session_id FROM sessions").fetchone()[0]

def test_index_page_renders(client):
    r = client.get("/")
    html = r.get_data(as_text=True)
    assert r.status_code == 200
    assert html.count('class="chip"') == 6
    assert "Between 45% and 50%" in html

def test_bust_session_can_finish_and_is_marked_bust(client, monkeypatch):
    start(client)
    force_pocket(monkeypatch, 3)
    client.post("/api/spin", json={"bet": 1000, "bet_type": "black"})
    r = client.post("/api/finish", json={"odds_after": ODDS_OPTIONS[0]})
    assert r.status_code == 200
    assert r.get_json()["summary"]["final_balance"] == 0
    assert storage.get_session(_only_session_id())["ended_by"] == "bust"

def test_history_view_only_counts_during_the_game(client):
    assert client.post("/api/history-view", json={}).status_code == 409