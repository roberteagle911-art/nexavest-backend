import os
import requests
import yfinance as yf
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

# Load environment variables (for local dev or Replit)
load_dotenv()

app = FastAPI(title="NexaVest Backend (Vercel)")

# Allow your frontend access
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

# ✅ Finnhub API key (from environment or default)
FINNHUB_API_KEY = os.getenv("FINNHUB_API_KEY", "YOUR_API_KEY")
FINNHUB_URL = "https://finnhub.io/api/v1/quote"


class AnalyzeRequest(BaseModel):
    symbol: str
    amount: float


@app.get("/")
def home():
    return {"status": "ok", "message": "Backend running successfully 🚀"}


@app.post("/analyze")
def analyze_stock(request: AnalyzeRequest):
    symbol = request.symbol.upper()
    amount = request.amount

    # Try fetching data from Finnhub
    try:
        response = requests.get(f"{FINNHUB_URL}?symbol={symbol}&token={FINNHUB_API_KEY}")
        data = response.json()
        if "c" not in data or data["c"] == 0:
            raise Exception("No data from Finnhub")

        current = data["c"]
        high = data["h"]
        low = data["l"]
        prev = data["pc"]

    except Exception:
        # Fallback using yfinance
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5d")
            current = hist["Close"].iloc[-1]
            high = hist["High"].iloc[-1]
            low = hist["Low"].iloc[-1]
            prev = hist["Close"].iloc[-2]
        except Exception:
            raise HTTPException(status_code=404, detail="Invalid symbol or no data available")

    # Calculate metrics
    volatility = round((high - low) / current, 3)
    expected_return = round((current - prev) / prev, 3)

    if volatility < 0.02:
        risk = "Low"
    elif volatility < 0.05:
        risk = "Medium"
    else:
        risk = "High"

    recommendation = f"{symbol} shows {risk.lower()} volatility with an expected return of {expected_return*100:.2f}%."

    return {
        "symbol": symbol,
        "current_price": round(current, 2),
        "expected_return": expected_return,
        "volatility": volatility,
        "risk_category": risk,
        "ai_recommendation": recommendation
    }
