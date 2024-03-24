"""This module manages the db using an ORM wrapper"""

from datetime import datetime
from sqlalchemy import (
    create_engine,
    inspect,
)
import pandas as pd
import json
import logging
from sqlalchemy.orm import sessionmaker


class DBLib:
    """Class to control the management of the database using sqlalchemy"""

    def __init__(self):
        self.create_engine()

    def create_engine(self):
        """Ensure we have a engine connection to the db"""
        try:
            engine = create_engine("sqlite:///SensorData.db")

            print("Database engine set up successfully")
            self.engine = engine
            
            self.setup_db()
        except Exception as exc:
            print(exc)
            return None

    def create_connection(self):
        """Ensure we have a direct connection to the db, try and do this in a singleton way"""
        try:
            connection = self.engine.connect()
            self.connection = connection
            return connection
        except Exception as exc:
            logging.error(exc)
            return None

    def setup_db(self):
        """The set up function will create the db tables if they don't already exist"""

        self.create_table()

        print("DB setup complete")

    # Table creation logic
    def create_table(self):
        """Table creation logic"""

        try:

            # Only run this if our db doesn't have the target table
            # Read JSON data from a file
            with open("data.json", "r") as file:
                json_data = json.load(file)

            # Normalize the JSON data into a DataFrame
            df = pd.DataFrame()
            for device_id, device_data in json_data.items():
                device_df = pd.json_normalize(device_data)
                device_df["device_id"] = device_id  # Add 'device_id' column
                df = pd.concat([df, device_df], ignore_index=True)

            # Set 'device_id' as the index
            df.set_index("device_id", inplace=True)

            # Ensure timestamp is in datetime format
            df["timestamp"] = pd.to_datetime(df["timestamp"])

            # Write data into the table in sqllite database
            df.to_sql("SensorData", self.engine)

        except Exception as exc:
            logging.debug("Sensor data error "+exc)
