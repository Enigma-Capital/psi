from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import random
import json
import time
import requests
import math
from typing import Dict, List, Tuple

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

DATA_FILE = "psi_stock_data.json"

# News with sentiment classifications (kept in memory, not saved to JSON)
NEWS_DATA: List[Tuple[str, float]] = [
    # Positive news (sentiment > 0)
    ("PSI's revolutionary algorithm shows unprecedented accuracy in recent tests!", 0.8),
    ("Major institutional investors showing strong interest in PSI technology.", 0.6),
    ("PSI's market prediction system outperforms traditional models.", 0.7),
    ("New partnership announcement boosts confidence in PSI's technology.", 0.75),
    ("PSI's latest upgrade receives widespread industry acclaim.", 0.65),
    
    # Negative news (sentiment < 0)
    ("Market volatility raises questions about PSI's adaptive capabilities.", -0.6),
    ("Competitors claim to have developed similar technology to PSI.", -0.5),
    ("Technical glitch in PSI's system causes temporary disruption.", -0.7),
    ("Regulatory concerns emerge around algorithmic trading systems.", -0.65),
    ("Market analysts express skepticism about PSI's recent performance.", -0.55),
    
    # Ambiguous news (sentiment near 0)
    ("PSI continues silent observation of market patterns.", 0.1),
    ("Unusual trading patterns detected by PSI's monitoring systems.", -0.1),
    ("PSI analysts reviewing recent market anomalies.", 0.0),
    ("Market participants await PSI's next move.", 0.2),
    ("PSI systems detect increased market activity.", -0.2)
]

# Market state (kept in memory, not saved to JSON)
MARKET_STATE = {
    "trend": 0.0,
    "volatility": 0.02,
    "momentum": 0.0,
    "cycle_phase": 0.0
}

def load_stock_data():
    try:
        with open(DATA_FILE, "r") as f:
            return json.load(f)
    except FileNotFoundError:
        return {"prices": [], "news": ""}

def save_stock_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_price_movement(base_price: float, sentiment: float) -> float:
    # Update market state
    MARKET_STATE["cycle_phase"] += random.uniform(0.01, 0.03)
    MARKET_STATE["trend"] = math.sin(MARKET_STATE["cycle_phase"]) * 0.3
    MARKET_STATE["volatility"] = max(0.01, min(0.04, MARKET_STATE["volatility"] + random.uniform(-0.005, 0.005)))
    MARKET_STATE["momentum"] = max(-0.5, min(0.5, MARKET_STATE["momentum"] + random.uniform(-0.1, 0.1)))

    trend_component = MARKET_STATE["trend"] * base_price * 0.02
    volatility_component = random.gauss(0, MARKET_STATE["volatility"] * base_price)
    momentum_component = MARKET_STATE["momentum"] * base_price * 0.01
    sentiment_component = sentiment * base_price * 0.03
    
    total_change = (
        trend_component +
        volatility_component +
        momentum_component +
        sentiment_component
    )

    micro_noise = random.uniform(-0.5, 0.5)
    return round(total_change + micro_noise, 2)

def fetch_real_stock():
    try:
        return random.uniform(95, 105)
    except:
        return 100

def generate_fake_stock():
    history = load_stock_data()
    base_price = fetch_real_stock()
    last_price = history["prices"][-1] if history["prices"] else base_price

    # Generate news and get sentiment
    current_sentiment = 0
    if random.random() < 0.2:
        news_item, sentiment = random.choice(NEWS_DATA)
        history["news"] = news_item  # Only save the news headline
        current_sentiment = sentiment  # Use sentiment for price calculation but don't save it
    
    # Generate new price based on sentiment and market factors
    price_change = generate_price_movement(last_price, current_sentiment)
    new_price = max(0.01, last_price + price_change)

    if len(history["prices"]) > 100:
        history["prices"].pop(0)

    history["prices"].append(round(new_price, 2))
    save_stock_data(history)
    return history

@app.get("/stocks")
def get_stock_data():
    return generate_fake_stock()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)