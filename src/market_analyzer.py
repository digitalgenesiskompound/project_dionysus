# market_analyzer.py

import json
from datetime import datetime
from price_analysis import fetch_price_history, analyze_price_history

class MarketAnalyzer:
    def __init__(self, api_client, min_profit=0.50, max_listing_price=100.00):
        self.api_client = api_client
        self.min_profit = min_profit
        self.max_listing_price = max_listing_price
        self.seen_ids = set() 

    def calculate_profit(self, buy_price, sell_price):
        csfloat_fee = sell_price * 0.05
        tax_buffer = sell_price * 0.05
        net_sell = sell_price - csfloat_fee - tax_buffer
        return net_sell - buy_price

    def save_deal(self, deal):
        try:
            with open("deals.json", "r") as f:
                existing = json.load(f)
        except (FileNotFoundError, json.decoder.JSONDecodeError):
            existing = []

        deal["buy_time"] = datetime.utcnow().isoformat()
        deal["status"] = "holding"
        existing.append(deal)

        with open("deals.json", "w") as f:
            json.dump(existing, f, indent=4)

    def analyze_listings(self, listings):
        opportunities = []

        for listing in listings:
            try:
                item = listing.get("item", {})
                ref_data = listing.get("reference", {})

                name = item.get("market_hash_name")
                if not name:
                    continue

                listing_id = listing.get("id")
                if not listing_id or listing_id in self.seen_ids:
                    continue
                self.seen_ids.add(listing_id)
                price = listing.get("price", 0) / 100

                predicted_price = ref_data.get("predicted_price", 0) / 100
                highest_buy_order = ref_data.get("highest_buy_order", 0) / 100

                # Pull graph data from CSFloat (your new power 🧠)
                points = fetch_price_history(name)
                history_stats = analyze_price_history(points, days=7)

                if history_stats is None:
                    continue  # not enough data

                avg_price = history_stats["avg_price"]
                volatility = history_stats["volatility"]
                avg_sales_per_day = history_stats["avg_sales_per_day"]

                # Add optional filters here
                if avg_sales_per_day < 0.5:
                    continue  # item doesn't sell often enough

                # Optional: Skip highly volatile items
                if volatility > 8:  # tune this threshold
                    continue

                # Use avg_price instead of predicted if it's more reliable
                if avg_price > 0:
                    target_price = avg_price
                elif predicted_price > 0:
                    target_price = predicted_price
                else:
                    continue  # no valid price anchor found

                flip_type = None
                profit = 0

                # Check for instant flip first
                if highest_buy_order > 0 and price < highest_buy_order:
                    profit = round((highest_buy_order * 0.95) - price, 2)
                    if profit >= self.min_profit:
                        flip_type = "instant"
                        target_price = highest_buy_order

                # Otherwise, future flip based on price history
                elif price < target_price:
                    profit = round(self.calculate_profit(price, target_price), 2)
                    if profit >= self.min_profit:
                        flip_type = "future"

                if flip_type:
                    print(f"✅ [{flip_type.upper()} FLIP] {name}")
                    print(f"  Listed: ${price:.2f}")
                    print(f"  Target: ${target_price:.2f}")
                    print(f"  📈 Projected Profit: ${profit:.2f}")
                    print(f"  📊 7-day avg = ${avg_price:.2f} | Volatility = ±${volatility:.2f} | Sales/day = {avg_sales_per_day}")

                    deal = {
                        "item_id": listing_id,
                        "name": name,
                        "price": price,
                        "target_price": target_price,
                        "flip_type": flip_type,
                        "profit": profit,
                        "avg_price_7d": avg_price,
                        "volatility": volatility,
                        "avg_sales": avg_sales_per_day
                    }

                    opportunities.append(deal)
                    self.save_deal(deal)

            except Exception as e:
                print(f"[ERROR] Skipping listing — {e}")
                continue

        return opportunities