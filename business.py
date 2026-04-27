import json
import os
import requests
from ai import get_trade_recommendations
from config import API_KEY

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
POSITIONS_FILE = os.path.join(BASE_DIR, "positions.json")
TRADES_FILE = os.path.join(BASE_DIR, "trades.json")
MOTHERSHIP_URL = "https://mothership-crg7hzedd6ckfegv.eastus-01.azurewebsites.net/make_trade"


def save_positions(positions):
    with open(POSITIONS_FILE, "w") as f:
        json.dump(positions, f, indent=2)


def load_positions():
    if not os.path.exists(POSITIONS_FILE):
        return []
    with open(POSITIONS_FILE, "r") as f:
        return json.load(f)


def save_trades(trades):
    with open(TRADES_FILE, "w") as f:
        json.dump(trades, f, indent=2)


def load_trades():
    if not os.path.exists(TRADES_FILE):
        return []
    with open(TRADES_FILE, "r") as f:
        return json.load(f)


def post_trades_to_mothership(run_id, trades):
    headers = {
        "x-api-key": API_KEY,
        "Content-Type": "application/json"
    }

    body = {
        "id": run_id,
        "trades": trades
    }

    response = requests.post(MOTHERSHIP_URL, json=body, headers=headers, timeout=20)
    return response


def analyze_tick(payload: dict, run_id: str) -> dict:
    incoming_positions = payload.get("Positions", [])
    market_summary = payload.get("Market_Summary", [])

    # Save current incoming positions immediately, per assignment expectations.
    save_positions(incoming_positions)

    market_lookup = {}
    for item in market_summary:
        market_lookup[item["ticker"]] = float(item["current_price"])

    unrealized_pnl = 0.0
    for position in incoming_positions:
        ticker = position["ticker"]
        quantity = float(position["quantity"])
        purchase_price = float(position["purchase_price"])

        if ticker in market_lookup:
            current_price = market_lookup[ticker]
            unrealized_pnl += (current_price - purchase_price) * quantity

    # Ask AI for trade recommendations
    decisions = get_trade_recommendations(payload)

    # Save recommendations to trade log
    save_trades(decisions)

    # Post recommendations to mothership
    mothership_response = post_trades_to_mothership(run_id, decisions)

    # If successful, overwrite local positions with returned Positions
    if mothership_response.status_code == 200:
        response_json = mothership_response.json()
        updated_positions = response_json.get("Positions", [])
        save_positions(updated_positions)
    else:
        # Keep existing saved positions if mothership fails
        response_json = {}
        updated_positions = load_positions()

    return {
        "result": "success",
        "summary": {
            "positions_evaluated": len(incoming_positions),
            "unrealized_pnl": unrealized_pnl
        },
        "decisions": decisions,
        "mothership_status": mothership_response.status_code,
        "mothership_response": response_json,
        "positions_after_trade": updated_positions
    }