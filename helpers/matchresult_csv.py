import pandas as pd
from typing import List
from models.timeline import TradeTimeline
from services.matcher import MatchResult

def trade_key(trade):
    if trade is None:
        return None
    return (
        trade.symbol,
        trade.trade_type,
        trade.quantity,
        round(trade.price, 4),
        trade.trade_time,
    )

def results_to_csv(
    timeline: TradeTimeline,
    match_results: List[MatchResult]
) -> pd.DataFrame:

    rows = []
    match_index = {}

    # --- Build match lookup ---
    for r in match_results:
        key_bt = trade_key(r.backtest_trade)
        key_lt = trade_key(r.live_trade)

        payload = {
            "flag": r.flag,
            "reason": r.reason,
            "time_diff": r.time_diff,
            "price_diff": r.price_diff,
            "matched": r.matched,
        }

        if r.matched:
            if key_bt:
                match_index[key_bt] = {**payload, "status": "MATCHED"}
            if key_lt:
                match_index[key_lt] = {**payload, "status": "MATCHED"}

        else:
            if r.backtest_trade and not r.live_trade:
                match_index[key_bt] = {**payload, "status": "MISS"}

            if r.live_trade and not r.backtest_trade:
                match_index[key_lt] = {**payload, "status": "MISS"}

    # --- Walk timeline ---
    for event in timeline.events:
        trade = event.trade
        info = match_index.get(trade_key(trade), {})

        rows.append({
            "time": event.time,
            "source": event.source,

            # classification
            # "status": info.get("status", "UNCLASSIFIED"),
            "status": info.get("flag"),
            "reason": info.get("reason"),

            # trade fields
            "symbol": trade.symbol,
            "trade_type": trade.trade_type,
            "quantity": trade.quantity,
            "price": trade.price,

            # diagnostics
            "time_diff": info.get("time_diff"),
            "price_diff": info.get("price_diff"),
            # "matched": info.get("matched"),
        })

    df = pd.DataFrame(rows)
    df.sort_values("time", inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df

def results_to_csv_split(
    match_results: List[MatchResult]
) -> pd.DataFrame:

    rows = []

    for r in match_results:
        lt = r.live_trade
        bt = r.backtest_trade

        rows.append({
            
            # -------- LIVE SIDE --------
            "live_symbol": lt.symbol if lt else None,
            "live_trade_type": lt.trade_type if lt else None,
            "live_quantity": lt.quantity if lt else None,
            "live_price": lt.price if lt else None,
            
            # middle reference time
            "time": lt.trade_time if lt else bt.trade_time if bt else None,

            # -------- BACKTEST SIDE --------
            "bt_symbol": bt.symbol if bt else None,
            "bt_trade_type": bt.trade_type if bt else None,
            "bt_quantity": bt.quantity if bt else None,
            "bt_price": bt.price if bt else None,

            # -------- MATCH INFO --------
            # "status": "MATCHED" if r.matched else "MISS",
            "flag": r.flag,
            "reason": r.reason,
            "time_diff": r.time_diff,
            "price_diff": r.price_diff,
        })

    df = pd.DataFrame(rows)
    df.sort_values("time", inplace=True)
    df.reset_index(drop=True, inplace=True)

    return df
