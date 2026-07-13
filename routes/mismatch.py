from fastapi import APIRouter, HTTPException
from services.flow import TradeMatchingFlowService, NoLiveTrades, NoBacktestTrades
from typing import Optional
from pydantic import BaseModel
from datetime import date
import traceback
from dependency import flow_service

router = APIRouter(prefix="/api", tags=["Find Leakage"])

# service = TradeMatchingFlowService()
# flow_service = flow_service

class LeakRequest(BaseModel):
    live_algo: str
    backtest_algo: str
    start_date: date
    end_date: date
    price_tolerance: float
    clientId: Optional[str] = None
    min_price_for_hedge: Optional[float] = None
    check_qnt: Optional[bool] = False
    broker: Optional[str] = None

@router.post('/leak')
def find_mismatch(payload: LeakRequest
):
  
    try:
        results = flow_service.reconcile(
            backtest_algo=payload.backtest_algo,
            live_algo=payload.live_algo,
            start_date=payload.start_date,
            end_date=payload.end_date,
            price_tolerance=payload.price_tolerance,
            clientId=payload.clientId,
            min_price_for_hedge=payload.min_price_for_hedge,
            check_qnt=payload.check_qnt,
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