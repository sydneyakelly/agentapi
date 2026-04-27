from flask import Flask, request, jsonify, render_template
import json
from config import API_KEY
from business import analyze_tick
from validators import validate_tick

app = Flask(__name__)


def is_authorized():
    return request.headers.get("apikey") == API_KEY


@app.route("/", methods=["GET"])
def home():
    return jsonify({"message": "Strategy AI Agent API is running"}), 200


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    if not is_authorized():
        return jsonify({"result": "failure", "message": "Unauthorized"}), 401

    try:
        return jsonify({"result": "success", "message": "Ready to Trade"}), 200
    except Exception as e:
        return jsonify({"result": "failure", "message": str(e)}), 500


@app.route("/tick/<id>", methods=["POST"])
def tick(id):
    if not is_authorized():
        return jsonify({"result": "failure", "message": "Unauthorized"}), 401

    if not request.is_json:
        return jsonify({
            "result": "failure",
            "message": "Invalid payload: Content-Type must be application/json"
        }), 400

    try:
        payload = request.get_json()
    except Exception:
        return jsonify({
            "result": "failure",
            "message": "Invalid payload: Malformed JSON"
        }), 400

    error = validate_tick(payload)
    if error:
        return jsonify({
            "result": "failure",
            "message": f"Invalid payload: {error}"
        }), 400

    try:
        result = analyze_tick(payload, id)
        return jsonify(result), 200
    except Exception as e:
        return jsonify({
            "result": "failure",
            "message": str(e)
        }), 500


@app.route("/dashboard", methods=["GET"])
def dashboard():
    try:
        try:
            with open("positions.json", "r") as f:
                positions = json.load(f)
        except Exception:
            positions = []

        try:
            with open("trades.json", "r") as f:
                trades = json.load(f)
        except Exception:
            trades = []

        return render_template("dashboard.html", positions=positions, trades=trades)

    except Exception as e:
        return f"Error loading dashboard: {str(e)}"


if __name__ == "__main__":
    app.run(debug=True)