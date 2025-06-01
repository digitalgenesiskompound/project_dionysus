# price_analysis.py
import requests
from urllib.parse import quote
import statistics

def fetch_price_history(item_name):
    url = f"https://csfloat.com/api/v1/history/{quote(item_name)}/graph"
    try:
        res = requests.get(url)
        res.raise_for_status()
        return res.json()  # list of daily points
    except Exception as e:
        print(f"[ERROR] Failed fetching graph data: {e}")
        return []

def analyze_price_history(points, days=7):
    if len(points) < days:
        return None  # not enough data

    recent = points[-days:]
    prices = [p["avg_price"] / 100 for p in recent]
    counts = [p["count"] for p in recent]

    avg_price = round(statistics.mean(prices), 2)
    volatility = round(statistics.stdev(prices), 2) if len(prices) > 1 else 0
    avg_sales = round(sum(counts) / len(counts), 2)

    return {
        "avg_price": avg_price,
        "volatility": volatility,
        "avg_sales_per_day": avg_sales,
        "days_analyzed": days
    }