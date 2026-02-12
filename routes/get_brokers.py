from pymongo import MongoClient, errors
from config import settings
from typing import Set
from fastapi import APIRouter, HTTPException, status


router = APIRouter(prefix="/api", tags=["Get Routes"])

@router.get("/get_brokers")
def get_brokers():
    try:
        client = MongoClient(
            settings.backoffice_mongo_uri,
            serverSelectionTimeoutMS=5000
        )    
        nb_db = client[settings.nb_backoffice_mongo_db]
        nb_collection = nb_db[settings.nb_backoffice_live_trade_collection]
        alpha_collection = nb_db[settings.alpha_backoffice_live_trade_collection]
        all_brokers_db = client[settings.all_brokers_backoffice_db]
        all_brokers_collection = all_brokers_db[settings.all_brokers_live_trade_collection]
        collections = [nb_collection, all_brokers_collection, alpha_collection]

        client.admin.command("ping")
    except errors.ServerSelectionTimeoutError:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Unable to connect to MongoDB"
        )
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Database initialization error: {str(e)}"
        )
    
    try:
        brokers: Set[str] = set()
        for collection in collections:
            distinct_brokers = collection.distinct("broker")
            brokers.update(distinct_brokers)

        return sorted(brokers)
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )