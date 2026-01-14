"""purpose: 
    Read data
    Validate data
    Return raw domain objects
"""

import pandas as pd
from pathlib import Path
from config import settings
from pymongo import MongoClient
from typing import List
from datetime import datetime, date, time, timezone, timedelta

from models.trade import BacktestRecord

class BacktestRepo:
    """Repository for handling backtest trade records"""

    def __init__(self):
        # self.base_path = Path(base_path)
        self.client = MongoClient(
            settings.finsage_mongo_uri, 
            tz_aware=True,
            tzinfo=timezone.utc)
        print(f"Connected to MongoDB at {settings.finsage_mongo_uri}")
        self.db = self.client[settings.finsage_mongo_db]
        print(f"Using database: {settings.finsage_mongo_db}")
        self.collection = self.db[settings.backtest_trade_collection]




    def load_trades(self, algoname: str, start_date: datetime, end_date: datetime) -> List[BacktestRecord]:
        """Load and normalize backtest trades for a given algorithm and date range."""        
        if start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")
        
        trades: List[BacktestRecord] = []
        # print(f"Loading backtest trades for algo: {algoname} from {start_date} to {end_date}")
        
        query = {
            "strategy": algoname,
            "ExitTime": {
                "$gte": datetime.combine(start_date, time.min, tzinfo=timezone.utc),
                "$lte": datetime.combine(end_date, time.max, tzinfo=timezone.utc)
            },
            "Key": {
                "$gte": datetime.combine(start_date, time.min, tzinfo=timezone.utc),
                "$lte": datetime.combine(end_date, time.max, tzinfo=timezone.utc)
            }
        }
        print(f"Querying backtest trades: For {algoname} from {start_date} to {end_date}")
        projection = {
            "_id": 0,
            "Key": 1,
            "ExitTime": 1,
            "Symbol": 1,
            "EntryPrice": 1,
            "ExitPrice": 1,
            "Quantity": 1,
            "PositionStatus": 1,
            "Pnl": 1,
            "ExitType": 1,
        }
        cursor = self.collection.find(query, projection).sort("Key", 1)
        for row in cursor:
            try:
                record = BacktestRecord(
                    EntryTime=row["Key"],
                    ExitTime=row["ExitTime"],
                    symbol=row["Symbol"],
                    EntryPrice=row["EntryPrice"],
                    ExitPrice=row["ExitPrice"],
                    Quantity=row["Quantity"],
                    PositionStatus=row["PositionStatus"],
                    Pnl=row["Pnl"],
                    ExitType=row["ExitType"],
                )

                trades.append(record)

            except Exception as e:
                print(f"Error parsing row: {row}. Error: {e}")
                raise e
        return trades