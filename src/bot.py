# bot.py

from dotenv import load_dotenv
from api_client import CsFloatAPIClient
from market_analyzer import MarketAnalyzer
import time
import logging
import os

load_dotenv()

# Set up logging
logging.basicConfig(
    filename="bot.log",
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)


def main():
    api_key = os.getenv("CSFLOAT_API_KEY")
    client = CsFloatAPIClient(api_key=api_key)

    analyzer = MarketAnalyzer(
        api_client=client,
        min_profit=0.50,
        max_listing_price=100.00
    )

    try:
        while True:
            print("Fetching market data...")
            logging.info("Fetching market data...")

            listings = client.get_market_data(max_pages=100)

            if listings:
                print(f"Analyzing {len(listings)} listings...")
                logging.info(f"Analyzing {len(listings)} listings...")
                deals = analyzer.analyze_listings(listings)

                if deals:
                    print(f"🔥 {len(deals)} profit opportunities found!")
                    logging.info(f"{len(deals)} profit opportunities found!")
                else:
                    print("No profitable deals found.")
                    logging.info("No profitable deals found.")
            else:
                print("No listings received from API.")
                logging.warning("No listings received from API.")

            time.sleep(300)

    except KeyboardInterrupt:
        print("Bot interrupted. Goodbye!")
        logging.info("Bot interrupted by user.")


if __name__ == "__main__":
    main()