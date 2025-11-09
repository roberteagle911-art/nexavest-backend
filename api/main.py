from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import yfinance as yf

app = FastAPI(title="NexaVest Backend (Vercel)")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

FINNHUB_API_KEY = "YOUR_API_KEY"
FINNHUB_URL = "https://finnhub.io/api/v1/quote"

class AnalyzeRequest(BaseModel):
    symbol: str
    amount: float

@app.get("/")
def home():
    return {"status": "ok", "message": "Backend running on Vercel"}

@app.post("/analyze")
def analyze_stock(request: AnalyzeRequest):
    symbol = request.symbol.upper().strip()
    if "." not in symbol:
        symbol += ".NS"

    try:
        res = requests.get(f"{FINNHUB_URL}?symbol={symbol}&token={FINNHUB_API_KEY}")
        data = res.json()
        if data and "c" in data and data["c"] != 0:
            current = data["c"]
            high, low, prev = data["h"], data["l"], data["pc"]
        else:
            raise Exception("No data from Finnhub")
    except Exception:
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5d")
            current = hist["Close"].iloc[-1]
            high = hist["High"].iloc[-1]
            low = hist["Low"].iloc[-1]
            prev = hist["Close"].iloc[-2]
        except Exception:
            raise HTTPException(status_code=404, detail="Invalid symbol or data unavailable")

    volatility = round((high - low) / current, 3)
    expected_return = round((current - prev) / prev, 3)

    if volatility < 0.02:
        risk = "Low"
    elif volatility < 0.05:
        risk = "Medium"
    else:
        risk = "High"

    return {
        "symbol": symbol,
        "current_price": round(current, 2),
        "expected_return": expected_return,
        "volatility": volatility,
        "risk_category": risk,
        "ai_recommendation": f"{symbol} shows {risk.lower()} risk and {expected_return*100:.2f}% expected return."
    }
