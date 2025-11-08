from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import yfinance as yf
import pandas as pd

app = FastAPI(title="NexaVest Backend", description="AI Risk & Return Data Engine", version="1.0")

class AnalyzeRequest(BaseModel):
    symbol: str
    amount: float

@app.get("/")
def home():
    return {"status": "ok", "message": "Welcome to NexaVest Backend"}

@app.post("/analyze")
def analyze_stock(data: AnalyzeRequest):
    try:
        df = yf.Ticker(data.symbol).history(period="1y")
        df["returns"] = df["Close"].pct_change()
        volatility = df["returns"].std() * (252 ** 0.5)
        annual_return = ((1 + df["returns"].mean()) ** 252) - 1
        risk = "Low" if volatility < 0.15 else "Medium" if volatility < 0.35 else "High"
        return {
            "symbol": data.symbol.upper(),
            "volatility": round(volatility, 3),
            "expected_return": round(annual_return, 3),
            "risk_category": risk
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
@app.post("/ai_recommend")
def ai_recommend(data: AnalyzeRequest):
    try:
        df = yf.Ticker(data.symbol).history(period="1y")
        df["returns"] = df["Close"].pct_change()
        volatility = df["returns"].std() * (252 ** 0.5)
        annual_return = ((1 + df["returns"].mean()) ** 252) - 1
        risk = "Low" if volatility < 0.15 else "Medium" if volatility < 0.35 else "High"

        # --- AI-style logic ---
        if risk == "Low":
            advice = f"{data.symbol} is a stable investment with low volatility and around {round(annual_return*100,1)}% annual return. Ideal for long-term holding (2-3 years)."
        elif risk == "Medium":
            advice = f"{data.symbol} shows moderate volatility and {round(annual_return*100,1)}% expected return. Suitable for medium-risk investors. Holding period: 12–18 months."
        else:
            advice = f"{data.symbol} is highly volatile with {round(annual_return*100,1)}% expected return. Suitable for short-term traders only. Consider limiting exposure."

        return {
            "symbol": data.symbol.upper(),
            "volatility": round(volatility, 3),
            "expected_return": round(annual_return, 3),
            "risk_category": risk,
            "ai_recommendation": advice
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
