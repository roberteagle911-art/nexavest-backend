import os
import requests
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI(title="NexaVest Backend")

# ✅ Allow frontend and localhost
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nexavest-frontend.vercel.app",
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "")
FINNHUB_URL = "https://finnhub.io/api/v1/quote"


class AnalyzeRequest(BaseModel):
    symbol: str
    amount: float


@app.get("/")
def home():
    return {"status": "ok", "message": "Backend running successfully 🚀"}


# ✅ NEW: allow GET too for browser test
@app.api_route("/api/analyze", methods=["GET", "POST"])
def analyze_stock(request: AnalyzeRequest = None, symbol: str = None, amount: float = None):
    if request:
        symbol = request.symbol.upper()
        amount = request.amount
    elif symbol:
        symbol = symbol.upper()
        amount = float(amount or 1000)
    else:
        raise HTTPException(status_code=400, detail="Missing symbol or amount")

    if not FINNHUB_API_KEY:
        raise HTTPException(status_code=500, detail="Missing FINNHUB_API_KEY environment variable")

    try:
        response = requests.get(f"{FINNHUB_URL}?symbol={symbol}&token={FINNHUB_API_KEY}")
        data = response.json()
        if "c" not in data or not data["c"]:
            raise Exception("No data returned")
        current = data["c"]
        high = data["h"]
        low = data["l"]
        prev = data["pc"]
    except Exception:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5d")
            current = hist["Close"].iloc[-1]
            high = hist["High"].iloc[-1]
            low = hist["Low"].iloc[-1]
            prev = hist["Close"].iloc[-2]
        except Exception:
            raise HTTPException(status_code=404, detail="Invalid stock symbol or no data found")

    volatility = round((high - low) / current, 3)
    expected_return = round((current - prev) / prev, 3)
    risk = "Low" if volatility < 0.02 else "Medium" if volatility < 0.05 else "High"

    return {
        "symbol": symbol,
        "current_price": round(current, 2),
        "expected_return": expected_return,
        "volatility": volatility,
        "risk_category": risk,
        "ai_recommendation": f"{symbol} shows {risk.lower()} volatility with expected return {expected_return*100:.2f}%."
        }
