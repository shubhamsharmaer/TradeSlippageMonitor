from models.timeline import TradeEvent, TradeTimeline
from models.trade import NormalizedTrade
from typing import List
from datetime import date, datetime

class TimelineMakerService:
    def timeline_builder(
            self,
            backtest_trades: List[NormalizedTrade],
            live_trades: List[NormalizedTrade],
            start_date: date,
            end_date: date
    ) -> TradeEvent:
        """For making timeline based on time and events (live and backtest trades basically)"""

        events: List[TradeEvent] = []

        for bt in backtest_trades:
            events.append(
                TradeEvent(
                    time=bt.trade_time,
                    source='backtest',
                    trade=bt
                )
            )

        for lt in live_trades:
            events.append(
                TradeEvent(
                    time=lt.trade_time,
                    source='live',
                    trade=lt
                )
            )
        events.sort(key=lambda e: e.time)
        return TradeTimeline(
            events=events,
            start_date=start_date,
            end_date=end_date
        )