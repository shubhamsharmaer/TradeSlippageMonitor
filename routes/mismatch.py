from fastapi import APIRouter, HTTPException
from services.flow import TradeMatchingFlowService
from typing import Optional
from datetime import date
import traceback

router = APIRouter(prefix="/api", tags=["Find Leakage"])

service = TradeMatchingFlowService()

@router.post('/leak')
def find_mismatch(
    live_algo: str,
    backtest_algo: str,
    start_date: date,
    end_date: date,
    clientId: Optional[str] = None
):

  
    try:
        results = service.reconcile(
            backtest_algo=backtest_algo,
            live_algo=live_algo,
            start_date=start_date,
            end_date=end_date,
            clientId=clientId
        )

        return {
            "status": "success",
            "data": results
        }
    
    except FileNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
        print(f"Error: {e}")

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
        print(f"Error: {e}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=traceback.format_exc())