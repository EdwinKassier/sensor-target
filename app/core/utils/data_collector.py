"""This module manages the main logic for the api """

import traceback
from datetime import datetime, timedelta
import requests
import pandas as pd
from sqlalchemy import text

import logging

from app.core.utils import DB


class DataCollector:
    """Driver class for the api"""

    def driver_logic(self):
        """Driver logic to run all business logic"""

        try:

            db = DB.DBLib()

            conn = db.create_connection()

            result = conn.execute(text("SELECT * FROM SensorData"))

            df_result = pd.DataFrame(result.fetchall(), columns=result.keys())

            api_result = df_result.to_json(orient="records")

            return api_result

        except Exception as e:
            logging.error("Table does not exist:", e)

            return False
