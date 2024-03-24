"""This module manages the db using raw sql"""

import sqlite3
from datetime import datetime
from dateutil import parser


class DataCache:
    """Class to control the management of the database using raw SQL"""

    def __init__(self, coin_symbol, investment):
        self.coin_symbol = coin_symbol
        self.investment = investment
        self.connection = self.create_connection()
        self.setup_db()

    # Set up db connection
    def create_connection(self):
        """Ensure we have a connection to the db"""
        try:
            conn = sqlite3.connect('DudeWheresMyLambo.db')

            # When returning queries, we want to convert results into dicts
            conn.row_factory = sqlite3.Row

            print("Database connected to successfully")
            return conn
        except Exception as exc:
            print(exc)

    def setup_db(self):
        """The set up function will create the db tables if they don't already exist"""

        self.create_table('RESULTS')
        self.create_table('OPENING_AVERAGE')
        self.create_table('LOGGING')

        print('DB setup complete')

    def create_table(self, table_name):
        """Table creation logic"""

        # We will have three tables, a RESULTS table to cache the results of a full query,
        # an OPENING_AVERAGE table to cache the average price of the coin within the first
        # month of its listing on the exchange and finally a LOGGING table to log and measure usage

        create_final_result_table = '''CREATE TABLE RESULTS
            (QUERY TEXT PRIMARY KEY     NOT NULL,
            NUMBERCOINS       REAL    NOT NULL,
            PROFIT            REAL     NOT NULL,
            GROWTHFACTOR      REAL     NOT NULL,
            LAMBOS            REAL     NOT NULL,
            INVESTMENT        INT     NOT NULL,
            SYMBOL            CHAR(50)     NOT NULL,
            GENERATIONDATE    TEXT     NOT NULL);'''

        create_opening_average_table = '''CREATE TABLE OPENING_AVERAGE
            (SYMBOL CHAR(50) PRIMARY KEY     NOT NULL,
            AVERAGE           REAL    NOT NULL);'''

        create_logging_table = '''CREATE TABLE LOGGING
            (QUERY_ID INTEGER PRIMARY KEY AUTOINCREMENT,
            SYMBOL            CHAR(50)     NOT NULL,
            INVESTMENT        INT     NOT NULL,
            GENERATIONDATE    TEXT     NOT NULL);'''

        try:
            if table_name == 'RESULTS':
                self.connection.execute(create_final_result_table)
            elif table_name == 'OPENING_AVERAGE':
                self.connection.execute(create_opening_average_table)
            elif table_name == 'LOGGING':
                self.connection.execute(create_logging_table)

        except Exception as exc:
            print(exc)

    def check_if_valid_final_result_exists(self):
        """Check if there exists a freshly cached result for the current query"""

        # Create cursor
        cur = self.connection.cursor()

        query = f"SELECT * from RESULTS WHERE QUERY = '{self.coin_symbol}-{self.investment}'"

        cur.execute(query)

        data = dict(result=[dict(r) for r in cur.fetchall()])

        result_list = data['result']

        if(len(result_list) > 0):
            # There exists a historical cache for this query

            # Checking how old the cached query is
            time_of_query = parser.parse(result_list[0]['GENERATIONDATE'])
            days_since_query = (datetime.now() - time_of_query).days

            # While there is a cached value, it needs to be fresh enough to use
            if(days_since_query < 7):
                return True
            else:
                # There exists a cached value, but it is stale
                return False
        else:
            # There doesn\'t exist a valid historical query
            return False

    def get_valid_final_result(self):
        """Get cached result for the current query"""

        # Create cursor
        cur = self.connection.cursor()

        query = f"SELECT * from RESULTS WHERE QUERY = '{self.coin_symbol}-{self.investment}'"

        cur.execute(query)

        data = dict(result=[dict(r) for r in cur.fetchall()])

        result_list = data['result']

        if len(result_list) > 0:
            return result_list[0]
        
        return {}

    def check_if_historical_cache_exists(self):
        """Check if we have already stored a cached version
        of the opening price data for the symbol"""

        # Create cursor
        cur = self.connection.cursor()

        query = f"SELECT * from OPENING_AVERAGE WHERE SYMBOL = '{self.coin_symbol}'"

        cur.execute(query)

        data = dict(result=[dict(r) for r in cur.fetchall()])

        result_list = data['result']

        if len(result_list) > 0:
            print(f'There exists a historical cache for this query {query}')
            return True

        print(f'There doesn\'t exist a valid historical query {query}')
        return False

    def get_historical_cache(self):
        """Get cached version of the opening price data for the symbol"""

        # Create cursor
        cur = self.connection.cursor()

        query = f"SELECT * from OPENING_AVERAGE WHERE SYMBOL = '{self.coin_symbol}'"

        cur.execute(query)

        data = dict(result=[dict(r) for r in cur.fetchall()])

        result_list = data['result']

        if len(result_list) > 0:
            return result_list[0]
   
        return {}

    def insert_into_logging(self):
        """Insert current query into the logging table"""

        combined_results = {'SYMBOL': self.coin_symbol,
                            'INVESTMENT': self.investment, 'GENERATIONDATE': datetime.now().isoformat()}

        columns = ', '.join(combined_results.keys())
        placeholders = ', '.join('?' * len(combined_results))
        sql = 'INSERT INTO LOGGING ({}) VALUES ({})'.format(
            columns, placeholders)
        values = [int(x) if isinstance(x, bool)
                  else x for x in combined_results.values()]

        try:
            self.connection.execute(sql, values)
            self.connection.commit()
            print('Insert into LOGGING successful')
        except Exception as exc:
            print(f'insert into LOGGING unsuccessful {exc}')

    def insert_into_result(self, result):
        """Insert final result from a query into the results table"""

        QUERY = f'{self.coin_symbol}-{self.investment}'

        combined_results = {**result, 'QUERY': QUERY}

        columns = ', '.join(combined_results.keys())
        placeholders = ', '.join('?' * len(combined_results))
        sql = 'INSERT OR REPLACE INTO RESULTS ({}) VALUES ({})'.format(
            columns, placeholders)
        values = [int(x) if isinstance(x, bool)
                  else x for x in combined_results.values()]

        try:
            self.connection.execute(sql, values)
            self.connection.commit()
            print('Insert into RESULTS successful')
        except Exception as exc:
            print(f'insert into RESULTS unsuccessful {exc}')

    def insert_into_opening_average(self, result):
        """Insert final result from data collector into the db"""

        combined_results = {**result, 'SYMBOL': self.coin_symbol}

        columns = ', '.join(combined_results.keys())
        placeholders = ', '.join('?' * len(combined_results))
        sql = 'INSERT OR REPLACE INTO OPENING_AVERAGE ({}) VALUES ({})'.format(
            columns, placeholders)
        values = [int(x) if isinstance(x, bool)
                  else x for x in combined_results.values()]

        try:
            self.connection.execute(sql, values)
            self.connection.commit()
            print('Insert into OPENING_AVERAGE successful')
        except Exception as exc:
            print(f'insert into OPENING_AVERAGE unsuccessful {exc}')
