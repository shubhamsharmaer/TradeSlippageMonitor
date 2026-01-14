from pymongo import MongoClient, errors
from config import settings
from typing import Set
from fastapi import APIRouter, HTTPException, status


router = APIRouter(prefix="/api", tags=["Get Routes"])

@router.get("/get_clients")
def get_clients():
    try:    
        client = MongoClient(
            settings.backoffice_mongo_uri,
            serverSelectionTimeoutMS=5000
            )
        db = client[settings.backoffice_mongo_db]
        collection = db[settings.backoffice_live_trade_collection]

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
        clients: Set[str] = set()

        distinct_clients = collection.distinct("clientID")
        clients.update(distinct_clients)

        return sorted(clients)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )