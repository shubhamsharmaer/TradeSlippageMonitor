from typing import Optional
from datetime import datetime

from pymongo import MongoClient
from config import settings


class NormalizedQuantity:
    def __init__(self):
        self.client = None
        self.collections = []

        if settings.is_demo_mode:
            return

        self.client = MongoClient(settings.backoffice_mongo_uri)
        print(f"Connected to MongoDB at {settings.backoffice_mongo_uri}")
        self.nb_db = self.client[settings.nb_backoffice_mongo_db]
        self.nb_collection = self.nb_db[settings.nb_backoffice_algo_collection]
        self.alpha_collection = self.nb_db[settings.alpha_backoffice_algo_collection]
        self.all_brokers_db = self.client[settings.all_brokers_backoffice_db]
        self.all_brokers_collection = self.all_brokers_db[settings.all_brokers_algo_collection]

        self.collections = [self.nb_collection, self.all_brokers_collection, self.alpha_collection]

    def get_normalized_quantity(
        self,
        algoname: str,
        original_quantity: int,
        clientID: str,
        trade_date: datetime,
        broker: str,
    ) -> Optional[int]:
        if settings.is_demo_mode:
            return original_quantity

        collections = self.collections
        query = {
            "broker": broker,
            "algoname": algoname,
            "clientID": clientID,
            "date": trade_date,
        }

        projection = {
            "_id": 0,
            "quantity_multiple": 1,
        }
        for collection in collections:
            doc = collection.find_one(query, projection)
            if doc and "quantity_multiple" in doc:
                quantity_multiple = int(doc["quantity_multiple"])
                normalize_quantity = original_quantity // quantity_multiple
                return normalize_quantity
        return original_quantity