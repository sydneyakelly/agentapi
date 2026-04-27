import json
import os
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def get_trade_recommendations(payload):
    """
    Return a list of trade decisions in this exact shape:
    [
      {"action": "SELL", "ticker": "AUTX", "quantity": 6},
      {"action": "BUY", "ticker": "MEDC", "quantity": 6},
      {"action": "STAY", "ticker": "HOMR", "quantity": 0}
    ]
    """

    system_prompt = """
You are a trading decision assistant.

You must return ONLY valid JSON.
Do not include markdown fences.
Do not include explanations.

Return a JSON array of objects with exactly these keys:
action, ticker, quantity

Rules:
- action must be one of: BUY, SELL, STAY
- ticker must be a stock ticker string
- quantity must be an integer
- If recommending STAY, quantity must be 0
- Use the user's current Positions, Market_Summary, and market_history
- Make a reasonable recommendation for each currently held position
- You may also recommend BUY for tickers in Market_Summary not currently held if they look attractive
"""

    user_prompt = f"""
Analyze this trading payload and return trade recommendations as a JSON array only.

Payload:
{json.dumps(payload, indent=2)}
"""

    response = client.responses.create(
        model="gpt-5-nano",
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt}
        ]
    )

    text = response.output_text.strip()

    try:
        parsed = json.loads(text)

        if not isinstance(parsed, list):
            return []

        cleaned = []
        for item in parsed:
            if not isinstance(item, dict):
                continue

            action = str(item.get("action", "STAY")).upper()
            ticker = str(item.get("ticker", "")).upper()
            quantity = item.get("quantity", 0)

            if action not in ["BUY", "SELL", "STAY"]:
                action = "STAY"

            try:
                quantity = int(quantity)
            except Exception:
                quantity = 0

            if action == "STAY":
                quantity = 0

            if ticker:
                cleaned.append({
                    "action": action,
                    "ticker": ticker,
                    "quantity": quantity
                })

        return cleaned

    except Exception:
        return []