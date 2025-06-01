# api_client.py

import requests

class CsFloatAPIClient:
    def __init__(self, api_key=None, base_url="https://csfloat.com/api/v1"):
        self.api_key = api_key
        self.base_url = base_url
        self.headers = {
            "Accept": "application/json"
        }
        if self.api_key:
            self.headers["Authorization"] = self.api_key

    def get_market_data(self, max_pages=100):
        """
        Retrieve multiple pages of CSFloat listings (50 per page).
        """
        all_listings = []
        for page in range(max_pages):
            url = f"{self.base_url}/listings?limit=50&page={page}&min_price=36&max_price=7278&type=buy_now"
            try:
                print(f"📄 Fetching page {page + 1}...")
                response = requests.get(url, headers=self.headers)
                response.raise_for_status()
                data = response.json()
                page_listings = data.get("data", [])

                if not page_listings:
                    break

                all_listings.extend(page_listings)
            except requests.RequestException as e:
                print(f"[ERROR] Failed to fetch page {page + 1}: {e}")
                break
        return all_listings

    def place_buy_order(self, item_id, price, quantity=1):
        """
        Place a placeholder buy order.
        NOTE: This will not work unless you are whitelisted.
        """
        endpoint = f"{self.base_url}/orders/buy"
        payload = {
            "item_id": item_id,
            "price": price,
            "quantity": quantity
        }
        try:
            response = requests.post(endpoint, json=payload, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"[ERROR] Failed to place buy order: {e}")
            return None