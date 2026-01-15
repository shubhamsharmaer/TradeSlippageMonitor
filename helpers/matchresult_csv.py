import pandas as pd
from typing import List
from services.matcher import MatchResult


def match_results_to_rows(matches: List[MatchResult]):
    rows = []

    for m in matches:
        bt = m.backtest_trade
        lt = m.live_trade

        if m.matched:
            status = "MATCHED"
            sort_time = min(bt.trade_time, lt.trade_time)
        elif bt and not lt:
            status = "MISSING_LIVE"
            sort_time = bt.trade_time
        elif lt and not bt:
            status = "EXTRA_LIVE"
            sort_time = lt.trade_time
        else:
            status = "UNKNOWN"

        rows.append({
            "sort_time": sort_time,
            "status": status,


            # ---- Backtest trade ----
            # "bt_trade_id": getattr(bt, "trade_id", None),
            "bt_symbol": getattr(bt, "symbol", None),
            "bt_trade_type": getattr(bt, "trade_type", None),
            "bt_trade_time": getattr(bt, "trade_time", None),
            "bt_qty": getattr(bt, "quantity", None),
            "bt_price": getattr(bt, "price", None),

            # ---- Live trade ----
            # "lt_trade_id": getattr(lt, "trade_id", None),
            "lt_symbol": getattr(lt, "symbol", None),
            "lit_trade_type": getattr(lt, "trade_type", None),
            "lt_trade_time": getattr(lt, "trade_time", None),
            "lt_qty": getattr(lt, "quantity", None),
            "lt_price": getattr(lt, "price", None),

            # ---- Match metadata ----
            # "score": m.score,
            "time_diff_sec": m.time_diff,
            "price_diff": m.price_diff,
            # "time_mismatch": m.time_mismatch,
            # "price_mismatch": m.price_mismatch,
            "reason": m.reason
        })

    return pd.DataFrame(rows)
