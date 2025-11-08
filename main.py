from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random

app = FastAPI()

# ✅ Add this section
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or ["https://nexavest-frontend.vercel.app"]
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
def root():
    return {"status": "ok", "message": "Welcome to NexaVest Backend"}

@app.post("/analyze")
def analyze_stock(request: dict):
    symbol = request.get("symbol")
    amount = request.get("amount")

    volatility = round(random.uniform(0.1, 0.5), 3)
    expected_return = round(random.uniform(0.05, 0.3), 3)
    risk_category = "High" if volatility > 0.4 else "Medium" if volatility > 0.2 else "Low"

    return {
        "symbol": symbol,
        "volatility": volatility,
        "expected_return": expected_return,
        "risk_category": risk_category
    }

@app.post("/ai_recommend")
def ai_recommend(request: dict):
    symbol = request.get("symbol")
    volatility = round(random.uniform(0.1, 0.5), 3)
    expected_return = round(random.uniform(0.05, 0.3), 3)
    risk_category = "High" if volatility > 0.4 else "Medium" if volatility > 0.2 else "Low"
    recommendation = (
        f"{symbol} shows {risk_category.lower()} volatility and "
        f"{expected_return*100:.1f}% expected return. "
        f"Suitable for {risk_category.lower()}-risk investors. "
        f"Holding period: 12–18 months."
    )
    return {
        "symbol": symbol,
        "volatility": volatility,
        "expected_return": expected_return,
        "risk_category": risk_category,
        "ai_recommendation": recommendation
    }
