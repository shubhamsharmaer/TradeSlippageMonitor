from fastapi import APIRouter, HTTPException
from services.flow import TradeMatchingFlowService, NoLiveTrades, NoBacktestTrades
from typing import Optional
from pydantic import BaseModel
from datetime import date
import traceback

router = APIRouter(prefix="/api", tags=["Find Leakage"])

service = TradeMatchingFlowService()

class LeakRequest(BaseModel):
    live_algo: str
    backtest_algo: str
    start_date: date
    end_date: date
    time_tolerance_minutes: int
    price_tolerance: float
    clientId: Optional[str] = None
    broker: Optional[str] = None

@router.post('/leak')
def find_mismatch(payload: LeakRequest
):

  
    try:
        results = service.reconcile(
            backtest_algo=payload.backtest_algo,
            live_algo=payload.live_algo,
            start_date=payload.start_date,
            end_date=payload.end_date,
            time_tolerance_minutes=payload.time_tolerance_minutes,
            price_tolerance=payload.price_tolerance,
            clientId=payload.clientId,
            broker=payload.broker
        )

        return {
            "status": "success",
            "data": results
        }
    

    except NoBacktestTrades as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except NoLiveTrades as e:
        raise HTTPException(status_code=400, detail=str(e))
    
    except FileNotFoundError as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=404, detail=str(e))

    except ValueError as e:
        print(f"Error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

    except Exception as e:
        print(f"Error: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=traceback.format_exc())