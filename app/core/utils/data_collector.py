"""This module manages the main logic for the api """

import traceback
from datetime import datetime, timedelta
import requests
import pandas as pd

# Import datacache class as a helper class
# This currently gives a linter error, but it does work as intended
from app.core.utils.data_cache import DataCache
from app.core.utils.data_cache_alchemy import DataCacheAlchemy



# Were I to use an api that requires an api key, this is how we would add it
# headers_dict =
# {'Accepts': 'application/json','X-CMC_PRO_API_KEY': 'cf1c4cb9-f50d-4d2c-8331-0ff5e2f0cc30',}
#r = requests.get('<MY_URI>', headers=headers_dict)


class DataCollector:
    """Driver class for the api"""

    def __init__(self, coin_symbol, investment):
        self.coin_symbol = coin_symbol
        self.investment = investment

    def convert_result_to_pd(self, raw):
        """Having been given a raw response from the api request,
        convert this into a pd dataframe"""

        # Convert raw response to a json representation
        ohlc_data = raw.json()['result']

        value = list(ohlc_data.values())[0]

        df = pd.DataFrame(value, columns=['timestamp', 'open', 'high', 'low', 'close', 'vwap', 'volume', 'count'])

        df = df.rename({'close': 'ClosePrice'}, axis='columns')

        df["ClosePrice"] = pd.to_numeric(df["ClosePrice"])

        df['CloseTime'] = pd.to_datetime(
                    df['timestamp'], unit='s')

        df['CloseTime'] = df['CloseTime'].astype(str)

        # make CloseTime Index of the data_frame
        df.set_index('CloseTime', inplace=True)

        return df

    def create_result_dict(self, average_start_price, average_end_price):
        """Create final result dict to be passed to the front end"""
        # init result dict - will become a json in the REST response
        result_dict = {}

        print(
            f'Create result dict average start price : {average_start_price}')

        # Number of coins purchased at the beginning
        number_of_coins = self.investment/average_start_price

        # What is our profit if we sold at the average price of the last month
        profit = round(
            ((number_of_coins*average_end_price)-self.investment), 2)

        # Growth factor of the initial investment
        growth_factor = round((profit/self.investment), 2)

        # number of lambos user could buy using this profit
        #  - assuming the price of an average lamborghini is $200000
        number_of_lambos = round((profit/200000), 2)

        result_dict.update({'NUMBERCOINS': number_of_coins, 'PROFIT': profit,
                            'GROWTHFACTOR': growth_factor, 'LAMBOS': number_of_lambos,
                            'INVESTMENT': self.investment, 'SYMBOL': self.coin_symbol,
                            'GENERATIONDATE': datetime.now().isoformat()})

        return result_dict

    def check_symbol_exists_on_exchange(self):
        """Check if we can get data about the given symbol on our target exchange"""
        try:
            check_symbol = (requests.get(
                f'https://api.kraken.com/0/public/OHLC?pair={self.coin_symbol}USD&interval=21600&since=1548111600')).json()

            if "error" in check_symbol and check_symbol["error"] == 'Instrument not found':
                return False

            return True
        except Exception as exc:
            print(exc)

            return False

    def driver_logic(self):
        """Driver logic to run all business logic"""

        try:

            dataCache = DataCacheAlchemy(self.coin_symbol, self.investment)

            # Irrelevant of what the user gave, we insert the query into the logging table
            dataCache.insert_into_logging()

            if self.check_symbol_exists_on_exchange() is False:
                return "Symbol doesn\'t exist"

            print('We should query the api')

            # Converting coin symbol to the lowercase version of itself
            coin_symbol = self.coin_symbol.lower()

            # Creating timestamps for the time period before the coin was listed and
            from_date = int(
                (datetime.now() - timedelta(weeks=1080)).timestamp())
            today_date = int(
                (datetime.now() - timedelta(weeks=12)).timestamp())

            # Here we are checking the datacache first to see if we even need to query the api
            # for the opening prices for the symbol, saving on long term time and api costs
            if dataCache.check_if_historical_cache_exists():
                print('Opening average cache exists for symbol')

                cached_historical_opening_data = dataCache.get_historical_cache()

                print(cached_historical_opening_data)

                average_start_price = cached_historical_opening_data

            else:
                print('We haven\'t seen this symbol before')

                data_raw_start = requests.get(
                    f'https://api.kraken.com/0/public/OHLC?pair={self.coin_symbol}USD&interval=21600&since=1548111600')

                # create pandas dataframe for the price data at the coins inception
                df_start = self.convert_result_to_pd(data_raw_start)

                # We are only looking at the first month
                df_start = df_start.head(4)

                # Average price for the starting period
                average_start_price = df_start["ClosePrice"].mean()

                print(df_start)

                opening_average_result = {
                    'SYMBOL': self.coin_symbol, 'AVERAGE': average_start_price}

                dataCache.insert_into_opening_average(
                    opening_average_result)

            # generating request urls to REST api
            data_raw_current = requests.get(
                f'https://api.kraken.com/0/public/OHLC?pair={self.coin_symbol}USD&interval=21600&since=1548111600')

            # create pandas dataframe for the price data at the moment
            df_end = self.convert_result_to_pd(data_raw_current)

            # We only want to look at the last four weeks of current data
            df_end = df_end.tail(4)

            # Average price for the current period
            average_end_price = df_end["ClosePrice"].mean()

            final_result = self.create_result_dict(
                average_start_price, average_end_price)

            dataCache.insert_into_result(final_result)

            print(df_end)
            print(average_end_price)

            print(final_result)

            return(final_result)
        except Exception as exc:
            print(traceback.format_exc())

            return False
