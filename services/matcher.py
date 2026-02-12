from datetime import datetime, time, timezone, timedelta
from typing import List, Optional, Literal
from models.trade import NormalizedTrade
# from helpers.quantity_norm import NormalizedQuantity
from pydantic import BaseModel
from logger_setup import logger
from models.timeline import TradeTimeline

# normalized_quantity_repo = NormalizedQuantity()

class MatchResult(BaseModel):
    backtest_trade: NormalizedTrade | None
    live_trade: NormalizedTrade | None
    matched: bool
    # score: float
    reason: str
    flag: str

    time_diff: float | None = None  
    price_diff: float | None = None
    time_mismatch: bool = False
    price_mismatch: bool = False

class MissingLiveTrade(BaseModel):
    result_type: Literal["missing"] = "missing"

    bt_trade: NormalizedTrade
    reason: str = "Live trade missing"

class ExtraLiveTrade(BaseModel):
    result_type: Literal["extra"] = "extra"

    lt_trade: NormalizedTrade
    reason: str = "Extra live trade"

MatchOutcome = MatchResult | MissingLiveTrade | ExtraLiveTrade

class TradeMatchingEngine:
    """Matches trades using a timeline-first approach.
    Time is already aligned by timeline, so matcher focuses on
    symbol, trade_type, quantity, price."""
    # def __init__(self, time_tolerance_minutes: int = 1, price_tolerance: float = 25.0):
    #     self.time_tolerance = timedelta(minutes=time_tolerance_minutes)
    #     self.price_tolerance = price_tolerance
    
    def match_trades(self, timeline: TradeTimeline, time_tolerance_minutes: int, price_tolerance: float) -> List[MatchResult]:
        self.time_tolerance = timedelta(minutes=time_tolerance_minutes)
        self.price_tolerance = price_tolerance

        results: List[MatchResult] = []

        current_time = None
        bt_bucket: List[NormalizedTrade] = []
        lt_bucket: List[NormalizedTrade] = []

        def flush_bucket(bucket_time):
            nonlocal results, bt_bucket, lt_bucket

            unmatched_lt = lt_bucket.copy()

            for bt in bt_bucket:
                match = None
                best_price_diff = None
                closest_lt = None

                # 1️⃣ Find eligible live trades
                for lt in unmatched_lt:
                    if (
                        lt.symbol == bt.symbol
                        and lt.trade_type == bt.trade_type
                        and (lt.quantity % bt.quantity == 0)
                    ):
                        price_diff = round(abs(lt.price - bt.price), 2)

                        # Track closest price
                        if best_price_diff is None or price_diff < best_price_diff:
                            best_price_diff = price_diff
                            closest_lt = lt

                # 2️⃣ Decide match
                if closest_lt:

                    match = closest_lt
                    unmatched_lt.remove(match)

                    if best_price_diff <= self.price_tolerance:

                        results.append(
                            MatchResult(
                                backtest_trade=bt,
                                live_trade=match,
                                matched=True,
                                flag="MATCH",
                                reason=f"Matched | price_diff={best_price_diff}",
                                time_diff=0.0,
                                price_diff=best_price_diff,
                                time_mismatch=False,
                                price_mismatch=False,
                            )
                        )
                    else:
                        results.append(
                            MatchResult(
                                backtest_trade=bt,
                                live_trade=match,
                                matched=False,
                                flag="PRICE MISMATCH",
                                reason=f"Price mismatch | price_diff={best_price_diff}",
                                time_diff=0.0,
                                price_diff=best_price_diff,
                                time_mismatch=False,
                                price_mismatch=True,
                            )
                        )

                else:
                    # 3️⃣ Diagnose miss reason
                    if best_price_diff is not None:
                        reason = f"Price mismatch {best_price_diff}"
                    else:
                        reason = "Live trade miss"

                    results.append(
                        MatchResult(
                            backtest_trade=bt,
                            live_trade=None,
                            matched=False,
                            flag="MISS",
                            reason=reason,
                            price_diff=best_price_diff,
                            price_mismatch=(best_price_diff is not None),
                        )
                    )

            # 4️⃣ Extra live trades
            for lt in unmatched_lt:
                results.append(
                    MatchResult(
                        backtest_trade=None,
                        live_trade=lt,
                        matched=False,
                        flag="MISS",
                        reason="Hedge | No eligible live trade",
                    )
                )

            bt_bucket.clear()
            lt_bucket.clear()

        # --- Main loop ---
        for event in timeline.events:
            if current_time is None:
                current_time = event.time

            if event.time != current_time:
                flush_bucket(current_time)
                current_time = event.time

            if event.source == "backtest":
                bt_bucket.append(event.trade)
            else:
                lt_bucket.append(event.trade)

        # Flush last bucket
        if bt_bucket or lt_bucket:
            flush_bucket(current_time)

        return results         