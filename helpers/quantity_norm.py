from typing import List, Optional
from pymongo import MongoClient
from config import settings

class NormalizedQuantity:
    def __init__(self):
        self.client = MongoClient(settings.backoffice_mongo_uri)
        print(f"Connected to MongoDB at {settings.backoffice_mongo_uri}")
        self.db = self.client[settings.backoffice_mongo_db]
        self.collection = self.db[settings.backoffice_algo_collection]
        # print(f"Using database: {settings.backoffice_mongo_db}")

    def get_normalized_quantity(self, algoname: str, original_quantity: int, clientID: str) -> Optional[int]:

        query = {
            "algoname": algoname,
            "clientID": clientID
        }

        projection = {
            "_id": 0,
            "quantity_multiple": 1
        }

        doc = self.collection.find_one(query, projection)
        if doc and "quantity_multiple" in doc:
            quantity_multiple = int(doc["quantity_multiple"])
            normalize_quantity = original_quantity // quantity_multiple
            return normalize_quantity
        return None