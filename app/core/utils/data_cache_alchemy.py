
"""This module manages the db using an ORM wrapper"""

from datetime import datetime
from sqlalchemy import (Column, DateTime, Float, Integer,
                        String, create_engine, inspect)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

Base = declarative_base()


class RESULTS(Base):
    """Class to represent a RESULTS object"""
    __tablename__ = 'RESULTS'

    id = Column(Integer, primary_key=True)
    QUERY = Column(String)
    NUMBERCOINS = Column(Float)
    PROFIT = Column(Float)
    GROWTHFACTOR = Column(Float)
    LAMBOS = Column(Float)
    INVESTMENT = Column(Float)
    SYMBOL = Column(String)
    GENERATIONDATE = Column(DateTime)


class OPENING_AVERAGE(Base):
    """Class to represent an OPENING_AVERAGE object"""
    __tablename__ = 'OPENING_AVERAGE'

    SYMBOL = Column(String, primary_key=True)
    AVERAGE = Column(Float)


class LOGGING(Base):
    """Class to represent an LOGGING object"""
    __tablename__ = 'LOGGING'

    id = Column(Integer, primary_key=True)
    QUERY_ID = Column(Integer)
    SYMBOL = Column(String)
    INVESTMENT = Column(Float)
    GENERATIONDATE = Column(DateTime)


class DataCacheAlchemy:

    """Class to control the management of the database using raw SQL"""

    def __init__(self, coin_symbol, investment):
        self.coin_symbol = coin_symbol
        self.investment = investment
        self.engine = self.create_connection()
        self.setup_db()

    def create_connection(self):
        """Ensure we have a connection to the db"""
        try:
            engine = create_engine('sqlite:///DudeWheresMyLambo.db')

            print("Database connected to successfully")
            return engine
        except Exception as exc:
            print(exc)
            return None

    def setup_db(self):
        """The set up function will create the db tables if they don't already exist"""

        self.create_table()

        print('DB setup complete')

    # Table creation logic
    def create_table(self):
        """Table creation logic"""

        # We will have three tables, a RESULTS table to cache the results of a full query,
        # an OPENING_AVERAGE table to cache the average price of the coin within the first
        # month of its listing on the exchange and finally a LOGGING table to log and measure usage

        try:
            Base.metadata.create_all(self.engine)

        except Exception as exc:
            print(exc)

    def check_if_valid_final_result_exists(self):
        """Check if there exists a freshly cached result for the current query"""

        print('Checking if value exists')

        try:

            create_session = sessionmaker(bind=self.engine)
            session = create_session()
            result = session.query(RESULTS).filter(RESULTS.QUERY.like(
                f'{self.coin_symbol}-{self.investment}')).first()

            if result != None:
                return True
            else:
                return False
        except Exception as exc:
            print(exc)
            return False

    def get_valid_final_result(self):
        """Get cached result for the current query"""

        try:

            create_session = sessionmaker(bind=self.engine)
            session = create_session()

            result = session.query(RESULTS).filter(RESULTS.QUERY.like(
                f'{self.coin_symbol}-{self.investment}')).first()

            if result is not None:
                return result[0]
            return {}
        except Exception as exc:
            print(exc)
            return {}

    def check_if_historical_cache_exists(self):
        """Check if we have already stored a cached version
        of the opening price data for the symbol"""

        query = f"SELECT * from OPENING_AVERAGE WHERE SYMBOL = '{self.coin_symbol}'"

        try:

            create_session = sessionmaker(bind=self.engine)
            session = create_session()

            result = session.query(OPENING_AVERAGE).filter(
                OPENING_AVERAGE.SYMBOL == str(self.coin_symbol)).first()

            if result is not None:
                print(result.SYMBOL, result.AVERAGE)
                print(
                    f'There exists a historical cache for this query {query}')
                return True
            else:
                print(f'There doesn\'t exist a valid historical query {query}')
                return False
        except Exception as exc:
            print(exc)
            print(f'There doesn\'t exist a valid historical query {query}')
            return False

    def get_historical_cache(self):
        """Get cached version of the opening price data for the symbol"""

        try:

            create_session = sessionmaker(bind=self.engine)
            session = create_session()

            results = session.query(OPENING_AVERAGE).filter(
                OPENING_AVERAGE.SYMBOL == str(self.coin_symbol)).first()

            if results is not None:
                print('Historical cache retrieval')
                print(f'Historic cache retrieved {results.AVERAGE}')
                return results.AVERAGE

            return {}
        except Exception as exc:
            print(exc)
            return {}

    def insert_into_logging(self):
        """Insert current query into the logging table"""

        combined_results = {'SYMBOL': self.coin_symbol,
                            'INVESTMENT': self.investment, 'GENERATIONDATE': datetime.now()}

        print(combined_results)

        new_item = LOGGING(
            SYMBOL=combined_results["SYMBOL"], INVESTMENT=combined_results["INVESTMENT"], GENERATIONDATE=combined_results["GENERATIONDATE"])

        Session = sessionmaker(bind=self.engine)
        session = Session()

        try:
            session.add(new_item)
            session.commit()
            print('Insert into LOGGING successful')
        except Exception as exc:
            print(f'insert into LOGGING unsuccessful {exc}')

    def insert_into_result(self, result):
        """Insert final result from a query into the results table"""

        query_string = f'{self.coin_symbol}-{self.investment}'

        combined_results = {**result, 'QUERY': query_string,
                            'GENERATIONDATE': datetime.now()}

        new_item = RESULTS(QUERY=query_string, NUMBERCOINS=combined_results["NUMBERCOINS"],
                           PROFIT=combined_results["PROFIT"], GROWTHFACTOR=combined_results[
                               "GROWTHFACTOR"], LAMBOS=combined_results["LAMBOS"],
                           INVESTMENT=combined_results["INVESTMENT"], SYMBOL=combined_results["SYMBOL"],
                           GENERATIONDATE=combined_results["GENERATIONDATE"])

        create_session = sessionmaker(bind=self.engine)
        session = create_session()

        try:
            session.add(new_item)
            session.commit()
            print('Insert into RESULTS successful')
        except Exception as exc:
            print(f'insert into RESULTS unsuccessful {exc}')

    def insert_into_opening_average(self, result):
        """Insert final result from data collector into the db"""

        combined_results = {**result, 'SYMBOL': self.coin_symbol}

        new_item = OPENING_AVERAGE(
            SYMBOL=combined_results["SYMBOL"], AVERAGE=combined_results["AVERAGE"])

        create_session = sessionmaker(bind=self.engine)
        session = create_session()

        try:
            session.add(new_item)
            session.commit()
            print('Insert into OPENING_AVERAGE successful')
        except Exception as exc:
            print(f'insert into OPENING_AVERAGE unsuccessful {exc}')

    def check_table_exists(self, table_name):
        """Check if queried table exists"""

        try:

            inspector = inspect(self.engine)
            table_exists = inspector.has_table(table_name)

            return table_exists
        except Exception as exc:
            print(exc)
