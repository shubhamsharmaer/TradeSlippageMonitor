from datetime import datetime, time, timezone, timedelta
from typing import List, Optional
from models.trade import NormalizedTrade
# from helpers.quantity_norm import NormalizedQuantity
from pydantic import BaseModel


# normalized_quantity_repo = NormalizedQuantity()
def quantity_matches(bt_qty: Optional[int], lt_qty: Optional[int]) -> bool:
    if bt_qty is None or lt_qty is None:
        return False
    
    if bt_qty == 0:
        return False
    return lt_qty % bt_qty == 0


class MatchResult(BaseModel):
    backtest_trade: NormalizedTrade | None
    live_trade: NormalizedTrade | None
    matched: bool
    score: float
    reason: str

    time_diff: float | None = None  
    price_diff: float | None = None
    time_mismatch: bool = False
    price_mismatch: bool = False

class TradeMatchingEngine:
    """Logic to match backtest trades with live trades."""
    def __init__(self, time_tolerance_minutes: int = 2, price_tolerance: float = 1.0):
        self.time_tolerance = timedelta(minutes=time_tolerance_minutes)
        self.price_tolerance = price_tolerance
    
    def match_trades(
        self,
        backtest_trades: List[NormalizedTrade],
        live_trades: List[NormalizedTrade]
    ) -> List[MatchResult]:
        try:
            unmatched_live_trades = live_trades.copy()
            results: List[MatchResult] = []

            for bt in backtest_trades:
                best_candidate = None
                best_score = 0.0
                reason = ""
                best_time_diff = None
                best_price_diff = None
                bool_time_mismatch = False
                bool_price_mismatch = False

                # SYMBOL, QUANTITY(NORMALIZED), TRADE TYPE
                candidate = [
                    lt for lt in unmatched_live_trades
                    if lt.symbol == bt.symbol
                    and lt.trade_type == bt.trade_type
                    and (lt.quantity % bt.quantity == 0)
                ]

                # TIME, PRICE MISMATCH CHECK
                for lt in candidate:
                    # --- time diff ---
                    time_diff = abs((lt.trade_time - bt.trade_time).total_seconds())
                    time_mismatch = time_diff > self.time_tolerance.total_seconds()

                    # --- price diff ---
                    price_diff = round(abs(lt.price - bt.price), 4)
                    price_mismatch = price_diff > self.price_tolerance

                    # if price_diff <= self.price_tolerance or time_mismatch:
                    if (price_diff <= self.price_tolerance
                        and time_diff <= self.time_tolerance.total_seconds()):
                        score = round(1.0 - (price_diff / self.price_tolerance), 4)

                        # if score > best_score:
                            # best_score = score
                        best_candidate = lt

                        best_time_diff = time_diff
                        best_price_diff = price_diff
                        bool_time_mismatch = time_mismatch
                        bool_price_mismatch = price_mismatch

                        reason = (
                                f"Matched | price_diff={price_diff}, "
                                f"time_diff={round(time_diff, 2)}s"
                            )

                if best_candidate:
                    unmatched_live_trades.remove(best_candidate)
                    results.append(
                        MatchResult(
                            backtest_trade=bt,
                            live_trade=best_candidate,
                            matched = True,
                            score=best_score,
                            reason=reason,
                            time_diff=best_time_diff,
                            price_diff=best_price_diff,
                            time_mismatch=bool_time_mismatch,
                            price_mismatch=bool_price_mismatch
                        )
                    )
                else:
                    results.append(
                        MatchResult(
                            backtest_trade=bt,
                            live_trade=None,
                            matched = False,
                            score=0.0,
                            reason = "Live trade missing"
                        )
                    )
            for lt in unmatched_live_trades:
                    results.append(
                        MatchResult(
                            backtest_trade=None,
                            live_trade=lt,
                            matched = False,
                            score=0.0,
                            reason = "Extra live unmatched trades"
                        )
                    )
            return results 
        except Exception as e:
                logger.error("❌ Something went wrong in matcher service")
        # print(results)