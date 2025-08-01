
from flask import Flask, request, jsonify
import json
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DB_FILE = "db.json"

def load_db():
    try:
        with open(DB_FILE, "r") as f:
            return json.load(f)
    except:
        return {"keys": [], "activations": []}

def save_db(db):
    with open(DB_FILE, "w") as f:
        json.dump(db, f, indent=2)

@app.route("/verify", methods=["POST"])
def verify():
    data = request.json
    key = data["key"]
    hwid = data["hwid"]
    db = load_db()

    for act in db["activations"]:
        if act["key"] == key:
            if act["hwid"] == hwid:
                return jsonify({"status": "valid"})
            else:
                return jsonify({"status": "invalid", "message": "Chiave già usata su altro dispositivo"})

    if key in db["keys"]:
        db["activations"].append({
            "key": key,
            "hwid": hwid,
            "status": "active",
            "timestamp": datetime.now().isoformat()
        })
        save_db(db)
        return jsonify({"status": "valid"})
    return jsonify({"status": "invalid", "message": "Chiave non valida"})

@app.route("/generate", methods=["POST"])
def generate():
    data = request.json
    key = data["key"]
    db = load_db()
    if key not in db["keys"]:
        db["keys"].append(key)
        save_db(db)
        return jsonify({"status": "ok"})
    return jsonify({"status": "exists"})

@app.route("/list", methods=["GET"])
def list_keys():
    db = load_db()
    return jsonify(db["activations"])

@app.route("/ban", methods=["POST"])
def ban():
    data = request.json
    db = load_db()
    for act in db["activations"]:
        if act["key"] == data["key"] and act["hwid"] == data["hwid"]:
            act["status"] = "banned"
            save_db(db)
            return jsonify({"status": "banned"})
    return jsonify({"status": "not_found"})

if __name__ == "__main__":
    app.run()
