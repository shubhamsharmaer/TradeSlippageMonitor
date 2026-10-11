from calendar import monthrange
from datetime import date, datetime, timezone

from fastapi import APIRouter, HTTPException, Query

from dependency import backtest_repo, live_repo

router = APIRouter(prefix="/api", tags=["Trade Calendar"])


@router.get("/trade_dates", response_model=dict[str, list[str]])
def get_trade_dates(
    live_algo: str,
    backtest_algo: str,
    month: str,
    client_id: str | None = None,
):
    try:
        month_start = date.fromisoformat(f"{month}-01")
        month_end = date(month_start.year, month_start.month, monthrange(month_start.year, month_start.month)[1])
    except ValueError as exc:
        raise HTTPException(status_code=400, detail="month must use YYYY-MM format") from exc

    trade_dates = set()

    for trade in backtest_repo.load_trades(backtest_algo, month_start, month_end):
        for trade_time in (trade.EntryTime, trade.ExitTime):
            if month_start <= trade_time.date() <= month_end:
                trade_dates.add(trade_time.date().isoformat())

    for trade in live_repo.load_trades(
        live_algo,
        month_start,
        month_end,
        clientId=client_id,
    ):
        trade_dates.add(datetime.fromtimestamp(trade.orderSentTime, timezone.utc).date().isoformat())

    return {"dates": sorted(trade_dates)}