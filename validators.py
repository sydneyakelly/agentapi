def validate_tick(payload):
    if not isinstance(payload, dict):
        return "Payload must be a JSON object"

    if "Positions" not in payload:
        return "Positions is required"
    if not isinstance(payload["Positions"], list) or len(payload["Positions"]) == 0:
        return "Positions must be a non-empty list"

    if "Market_Summary" not in payload:
        return "Market_Summary is required"
    if not isinstance(payload["Market_Summary"], list) or len(payload["Market_Summary"]) == 0:
        return "Market_Summary must be a non-empty list"

    if "market_history" not in payload:
        return "market_history is required"
    if not isinstance(payload["market_history"], list):
        return "market_history must be a list"

    for p in payload["Positions"]:
        if not isinstance(p, dict):
            return "Each Positions item must be an object"

        required = ["ticker", "quantity", "purchase_price"]
        for key in required:
            if key not in p:
                return f"Each position must include {key}"

        if not isinstance(p["ticker"], str):
            return "Position ticker must be a string"
        if not isinstance(p["quantity"], (int, float)):
            return "Position quantity must be numeric"
        if not isinstance(p["purchase_price"], (int, float)):
            return "Position purchase_price must be numeric"

    for m in payload["Market_Summary"]:
        if not isinstance(m, dict):
            return "Each Market_Summary item must be an object"

        required = ["ticker", "current_price", "category"]
        for key in required:
            if key not in m:
                return f"Each market summary item must include {key}"

        if not isinstance(m["ticker"], str):
            return "Market_Summary ticker must be a string"
        if not isinstance(m["current_price"], (int, float)):
            return "Market_Summary current_price must be numeric"
        if not isinstance(m["category"], str):
            return "Market_Summary category must be a string"

    for h in payload["market_history"]:
        if not isinstance(h, dict):
            return "Each market_history item must be an object"

        required = ["ticker", "price", "day"]
        for key in required:
            if key not in h:
                return f"Each market history item must include {key}"

        if not isinstance(h["ticker"], str):
            return "market_history ticker must be a string"
        if not isinstance(h["price"], (int, float)):
            return "market_history price must be numeric"
        if not isinstance(h["day"], str):
            return "market_history day must be a string"

    return None