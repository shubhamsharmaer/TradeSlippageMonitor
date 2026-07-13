from pymongo import MongoClient, errors
from typing import Set
from config import settings
from fastapi import APIRouter, HTTPException, status
from pymongo.errors import ServerSelectionTimeoutError
from dependency import backtest_repo

router = APIRouter(prefix="/api", tags=["Get Routes"])


@router.get('/get_bt_algos', response_model=list[str])
def get_bt_algo():
    # try:
    #     client = MongoClient(
    #         settings.finsage_mongo_uri,
    #         serverSelectionTimeoutMS=5000
    #         )
    #     db = client[settings.finsage_mongo_db]
    #     auto_db = client[settings.auto_backtest_db]
    #     auto_collection = auto_db[settings.auto_backtest_collection]
    #     collection = db[settings.backtest_trade_collection]

    #     combined_collection = [auto_collection, collection]

    #     client.admin.command("ping")
    
    # except errors.ServerSelectionTimeoutError:
    #     raise HTTPException(
    #         status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
    #         detail="Unable to connect to MongoDB"
    #     )

    # except Exception as e:
    #     raise HTTPException(
    #         status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
    #         detail=f"Database initialization error: {str(e)}"
    #     )
    try:
        # bt_algos: Set(str) = set() 
        # for collection in combined_collection:
        #     distinct_algos = collection.distinct("strategy")
        #     bt_algos.update(distinct_algos)
        # return bt_algos

        return backtest_repo.list_strategies()
    except ServerSelectionTimeoutError as e:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail=f"MongoDB Error: {str(e)}"
        )    
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Internal Server Error: {str(e)}"
        )
    