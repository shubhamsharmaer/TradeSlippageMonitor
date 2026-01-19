import pandas as pd
from models.timeline import TradeTimeline
from typing import List


def timeline_rows(timelines: List[TradeTimeline]) -> pd.DataFrame:
    rows = []

    for timeline in timelines:
        for event in timeline.events:
            trade = event.trade

            rows.append({
                # "timeline_start": timeline.start_date,
                # "timeline_end": timeline.end_date,

                "event_time": event.time,
                "source": event.source,

                # trade details
                # "trade_id": trade.trade_id,
                "algoname": trade.algoname,
                "symbol": trade.symbol,
                "clientID": trade.clientID,
                "trade_type": trade.trade_type,
                "price": trade.price,
                "quantity": trade.quantity,
                "trade_time": trade.trade_time,
                # "trade_source": trade.source,   # backtest / live
            })

    df = pd.DataFrame(rows)

    # 🔑 VERY IMPORTANT: sort by datetime
    df.sort_values(by="event_time", inplace=True)

    return df
