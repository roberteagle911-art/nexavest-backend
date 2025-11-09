from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import requests
import yfinance as yf

app = FastAPI(title="NexaVest Backend (Vercel)")

# ✅ Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "https://nexavest-frontend.vercel.app",  # your frontend domain
        "http://localhost:5173"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ✅ Replace with your Finnhub API Key
FINNHUB_API_KEY = "d47qudpr01qk80bi464gd47qudpr01qk80bi4650"
FINNHUB_URL = "https://finnhub.io/api/v1/quote"

class AnalyzeRequest(BaseModel):
    symbol: str
    amount: float

@app.get("/")
def home():
    return {"status": "ok", "message": "Backend running on Vercel"}

@app.post("/analyze")
def analyze_stock(request: AnalyzeRequest):
    symbol = request.symbol.upper()
    amount = request.amount

    try:
        # 🔹 Try fetching live data from Finnhub
        response = requests.get(f"{FINNHUB_URL}?symbol={symbol}&token={FINNHUB_API_KEY}")
        data = response.json()
        if "c" not in data or data["c"] == 0:
            raise Exception("No data from Finnhub")

        current = data["c"]
        high = data["h"]
        low = data["l"]
        prev = data["pc"]

    except Exception:
        # 🔹 Fallback: yfinance
        try:
            stock = yf.Ticker(symbol)
            hist = stock.history(period="5d")
            current = hist["Close"].iloc[-1]
            high = hist["High"].iloc[-1]
            low = hist["Low"].iloc[-1]
            prev = hist["Close"].iloc[-2]
        except Exception:
            raise HTTPException(status_code=404, detail="Invalid symbol or no data")

    # 📊 Calculations
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
        "ai_recommendation": f"{symbol} shows {risk.lower()} volatility with expected return {expected_return*100:.2f}%."
    }
