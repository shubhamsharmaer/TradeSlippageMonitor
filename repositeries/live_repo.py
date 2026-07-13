from typing import List, Optional, Set
from datetime import datetime, date, timedelta

from pymongo import MongoClient
from config import settings
from models.trade import LiveTradeRecord
from logger_setup import logger


class LiveTradeRepo:
    """Repository for fetching live trades from MongoDB"""

    def __init__(self):
        self.client = MongoClient(settings.backoffice_mongo_uri)
        # self.client = MongoClient(settings.mongo_uri)
        # self.db = self.client[settings.mongo_db]

        logger.info(f"✅ Connected to Live Trade MongoDB")
        self.nb_db = self.client[settings.nb_backoffice_mongo_db]
        self.nb_collection = self.nb_db[settings.nb_backoffice_live_trade_collection]
        self.alpha_collection = self.nb_db[settings.alpha_backoffice_live_trade_collection]
        logger.info(f"✅ Connected to NB Trade MongoDB")

        self.all_brokers_db = self.client[settings.all_brokers_backoffice_db]
        self.all_brokers_collection = self.all_brokers_db[settings.all_brokers_live_trade_collection]
        logger.info(f"✅ Connected to All Brokers Trade MongoDB")

        # append collection in one array
        self.collections = [self.nb_collection, self.all_brokers_collection, self.alpha_collection]


    # def _get_collection(self, start_date: date, end_date: date):
    #     if start_date > end_date:
    #         raise ValueError("start_date must be before or equal to end_date")
        
    #     all_collections = set(self.db.list_collection_names())
    #     collections = []
    #     current_date = start_date

    #     while current_date <= end_date:
    #         collection_name = f"final_response_{current_date.strftime('%Y-%m-%d')}"
    #         if collection_name in all_collections:
    #             collections.append(self.db[collection_name])
    #             # print(f"Using collection: {collection_name}")
    #         else:
    #             logger.warning(f"Collection {collection_name} does not exist.")
    #             print(f"")
    #         current_date += timedelta(days=1)
    #     return collections

    def list_algonames(self) -> List[str]:
        """Fetch all unique algorithm names."""
        algonames = set()
        for collection in self.collections:
            algonames.update(collection.distinct("algoname"))
        return sorted(algonames)
    
    def list_clients(self) -> List[str]:
        """Fetch all unique client IDs."""
        clients = set()
        for collection in self.collections:
            clients.update(collection.distinct("clientID"))
        return sorted(clients)
    
    def list_brokers(self) -> List[str]:
        """Fetch all unique brokers."""
        brokers = set()
        for collection in self.collections:
            brokers.update(collection.distinct("broker"))
        return sorted(brokers)


    def _get_distinct_clients(self, algoname: str, start_date: date, end_date: date) -> List[str]:
        collections = self.collections
        start_ts = datetime.combine(start_date, datetime.min.time()).timestamp()
        end_ts = datetime.combine(end_date, datetime.max.time()).timestamp()

        query = {
            "algoname": algoname,
            "orderStatus": "Filled",
            "orderSentTime": {
                "$gte": start_ts,
                "$lte": end_ts
            }
        }
        
        # projection = {
        #     "_id": 0,
        #     "clientID": 1
        # }
        clients: Set[str] = set()

        for collection in collections:
            distinct_clients = collection.distinct("clientID", query)
            clients.update(distinct_clients)

        return sorted(clients)
    
    def _get_distinct_brokers(self, algoname: str, start_date: date, end_date: date) -> List[str]:
        """Fetch distinct brokers for a given algo and date range."""
        # collections = self._get_collection(start_date, end_date)
        collections = self.collections
        start_ts = datetime.combine(start_date, datetime.min.time()).timestamp()
        end_ts = datetime.combine(end_date, datetime.max.time()).timestamp()

        query = {
            "algoname": algoname,
            "orderStatus": "Filled",
            "orderSentTime": {
                "$gte": start_ts,
                "$lte": end_ts
            }
        }
        
        brokers: Set[str] = set()

        for collection in collections:
            distinct_brokers = collection.distinct("broker", query)
            brokers.update(distinct_brokers)

        return sorted(brokers)

    def load_trades(self, algoname: str, start_date: date, end_date: date, clientId: str, broker: str) -> List[LiveTradeRecord]:
        """Load live trades for a given algo, client, and date range."""
        # collections = self._get_collection(start_date, end_date)
        collections = self.collections
        trades: List[LiveTradeRecord] = []
        
        start_ts = datetime.combine(start_date, datetime.min.time()).timestamp()
        end_ts = datetime.combine(end_date, datetime.max.time()).timestamp()

        
        query = {
                "broker": broker,
                "algoname": algoname,
                "clientID": clientId,
                "orderStatus": "Filled",
                "orderSentTime": {
                    "$gte": start_ts,
                    "$lte": end_ts
                }
        }

        projection = {
            "_id": 0,
            "quantity": 1,
            "algoname": 1,
            "symbol": 1,
            "buy_sell": 1,
            "orderSentTime": 1,
            "orderStatus": 1,
            "OrderAverageTradedPrice": 1,
            "clientID": 1,
            "broker": 1
        }

        # if clientId:
        #     query["clientID"] = clientId
        
        logger.info(f"🔽 Fetching Live trades: Client: {clientId} | Algo: {algoname} from {start_date} to {end_date}")
        for collection in collections:
            cursor = collection.find(query, projection).sort("orderSentTime", 1)
                
            for doc in cursor:
                adjusted_orderSentTime = doc["orderSentTime"] + 19800  # Adjusting for IST to UTC
                doc["orderSentTime"] = adjusted_orderSentTime
                try:
                    record = LiveTradeRecord(**doc)
                    trades.append(record)
                except Exception as e:
                    print(f"Error parsing document: {doc}. Error: {e}")
                    logger.error("❌ Something went wrong in live trades fetching")
                    raise e
        logger.info(f"✅ All Live trades fetched")
        return trades