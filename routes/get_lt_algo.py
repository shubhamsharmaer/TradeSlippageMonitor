from pymongo import MongoClient, errors
from typing import Set
from config import settings
from fastapi import APIRouter, HTTPException, status

router = APIRouter(prefix="/api", tags=["Get Routes"])

@router.get('/get_lt_algos')
def get_lt_algos():
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
        lt_algos: Set(str) = set()

        distinct_algos = collection.distinct("algoname")
        lt_algos.update(distinct_algos)

        return lt_algos
    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )
     