from flask import Flask, request, jsonify
import json, os
from pathlib import Path

app = Flask(__name__)

# Use Render's persistent disk if you enable it (recommended)
DATA_FILE = Path(os.environ.get("DATA_FILE", "highscores.json"))
MAX_SCORES = 10

def load_scores():
    if not DATA_FILE.exists():
        return {"highscores": []}
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_scores(data):
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=2)

@app.route("/highscores", methods=["GET"])
def get_highscores():
    return jsonify(load_scores())

@app.route("/submit", methods=["POST"])
def submit_score():
    data = request.get_json()
    if not data or "initials" not in data or "score" not in data:
        return {"error": "Invalid payload"}, 400

    initials = str(data["initials"])[:3].upper()
    score = int(data["score"])

    scores = load_scores()
    scores["highscores"].append({"initials": initials, "score": score})
    scores["highscores"] = sorted(scores["highscores"], key=lambda x: x["score"], reverse=True)[:MAX_SCORES]
    save_scores(scores)

    return {"ok": True}

# Local run only (Render uses gunicorn)
if __name__ == "__main__":
    port = int(os.environ.get("PORT", "5000"))
    app.run(host="0.0.0.0", port=port, debug=True)