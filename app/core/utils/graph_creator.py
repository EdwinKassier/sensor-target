"""This module manages the logic to get historical data for a symbol"""
from datetime import datetime, timedelta
import requests
import pandas as pd


# Were I to use an api that requires an api key, this is how we would add it
# headers_dict =
# {'Accepts': 'application/json','X-CMC_PRO_API_KEY': 'cf1c4cb9-f50d-4d2c-8331-0ff5e2f0cc30',}
#r = requests.get('<MY_URI>', headers=headers_dict)


class GraphCreator:
    """Helper class to get historical data"""

    def __init__(self, coin_symbol):
        self.coin_symbol = coin_symbol

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

        return df

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
        """Driver logic of the class to retrieve historical data"""

        try:

            if self.check_symbol_exists_on_exchange() is False:
                return "Symbol doesn\'t exist"
            print('We should query the api')

            # Creating timestamps for the time period before the coin was listed and
            from_date = int(
                (datetime.now() - timedelta(weeks=1080)).timestamp())
            # today_date = int( (datetime.now() - timedelta(weeks=12)).timestamp())

            # generating request urls to REST api
            data_raw_current = requests.get(
                f'https://api.kraken.com/0/public/OHLC?pair={self.coin_symbol}USD&interval=21600&since=1548111600')

            # create pandas dataframe for the price data at the moment
            data_frame = self.convert_result_to_pd(data_raw_current)

            # Remove two columns name is 'C' and 'D'
            data_frame = data_frame.drop(['open', 'high', 'timestamp',
                                          'low', 'volume', 'vwap','count'], axis=1)

            # Rename columns for frontend
            data_frame = data_frame.rename(
                {'CloseTime': 'x', 'ClosePrice': 'y'}, axis='columns')

            data_frame = data_frame.to_json(orient="records")

            print(data_frame)

            return data_frame
        except Exception as exc:
            print(exc)
