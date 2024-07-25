import asyncio
import aiohttp
import sys
from datetime import datetime, timedelta

API_URL = "https://api.privatbank.ua/p24api/exchange_rates?date=01.12.2014"

class ExchangeRateFetcher:
    def __init__(self, session):
        self.session = session

    async def fetch_rate_for_date(self, date):
        url = f"{API_URL}{date.strftime('%d.%m.%Y')}"
        async with self.session.get(url) as response:
            if response.status != 200:
                raise Exception(f"Error fetching data for {date.strftime('%d.%m.%Y')}: {response.status}")
            return await response.json()

class ExchangeRateProcessor:
    def process_rates(self, data):
        date = data['date']
        rates = {entry['ccy']: {'sale': entry['saleRate'], 'purchase': entry['purchaseRate']}
                 for entry in data['exchangeRate'] if entry['ccy'] in ['EUR', 'USD']}
        return {date: rates}

async def main(days):
    async with aiohttp.ClientSession() as session:
        fetcher = ExchangeRateFetcher(session)
        processor = ExchangeRateProcessor()

        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)

        results = []
        for i in range(days):
            date = end_date - timedelta(days=i)
            try:
                data = await fetcher.fetch_rate_for_date(date)
                processed_data = processor.process_rates(data)
                results.append(processed_data)
            except Exception as e:
                print(e)

        print(results)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python main.py <number_of_days>")
        sys.exit(1)

    try:
        days = int(sys.argv[1])
        if not (1 <= days <= 10):
            raise ValueError
    except ValueError:
        print("The number of days must be an integer between 1 and 10.")
        sys.exit(1)

    asyncio.run(main(days))
