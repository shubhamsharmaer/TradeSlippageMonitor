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
        unmatched_live_trades = live_trades.copy()
        results: List[MatchResult] = []

        for bt in backtest_trades:
            best_candidate = None
            best_score = 0.0
            reason = ""

            candidate = [
                lt for lt in unmatched_live_trades
                if lt.symbol == bt.symbol
                and lt.trade_type == bt.trade_type
                and abs(lt.trade_time - bt.trade_time) <= self.time_tolerance
                # and quantity_matches(bt.quantity, lt.quantity)
                and (bt.quantity % lt.quantity == 0)
            ]

            for lt in candidate:
                original_price_diff = abs(lt.price - bt.price)
                price_diff = round(original_price_diff, 4)
                if price_diff <= self.price_tolerance:
                    original_score = 1.0 - (price_diff / self.price_tolerance)
                    score = round(original_score, 4)
                    if score > best_score:
                        best_score = score
                        best_candidate = lt
                        reason = f" Matched with price diff {price_diff}"

            if best_candidate:
                unmatched_live_trades.remove(best_candidate)
                results.append(
                    MatchResult(
                        backtest_trade=bt,
                        live_trade=best_candidate,
                        matched = True,
                        score=best_score,
                        reason = reason
                    )
                )
            else:
                results.append(
                    MatchResult(
                        backtest_trade=bt,
                        live_trade=None,
                        matched = False,
                        score=0.0,
                        reason = " Live trade missing"
                    )
                )

        for lt in unmatched_live_trades:
            results.append(
                MatchResult(
                    backtest_trade=None,
                    live_trade=lt,
                    matched = False,
                    score=0.0,
                    reason = " Extra live unmatched trades"
                )
            )
        # print(results)
        return results 