from typing import List
from models.mismatch import TradeMismatch, MismatchReport
from services.matcher import MatchResult
from datetime import date, timedelta

class MismatchDetector:
    def __init__(self, time_threshold: int = 2, price_threshold: float = 1.0):
        self.time_threshold = timedelta(minutes=time_threshold)
        self.price_threshold = price_threshold

    def analyze(self, matches: List[MatchResult]) -> MatchResult:
        missing = [] # in backtest but not in live
        extra = []  # in live but not in backtest
        time_mismatch = []
        price_mismatch = []

        for m in matches:
            if m.backtest_trade and not m.live_trade:
                missing.append(self._missing_trade(m))
            elif not m.backtest_trade and m.live_trade:
                extra.append(self._extra_trade(m))
            elif m.backtest_trade and m.live_trade:
                self._analyze_deviation(m, time_mismatch, price_mismatch)
        
        summary = self._build_summary(matches, missing, extra, time_mismatch, price_mismatch)

        return MismatchReport(
            extra_trades=extra,
            missing_trades=missing,
            time_mismatches=time_mismatch,
            price_mismatches=price_mismatch,
            summary=summary
        )

    def _missing_trade(self, match: List[MismatchReport]) -> TradeMismatch:
        return TradeMismatch(
            trade=self.backtest_trade,
            mismatch_type="MISSING TRADE",
            expected="Live Execution",
            actual=None
        )

    def _extra_trade(self, match: List[MismatchReport]) -> TradeMismatch:
        return TradeMismatch(
            trade=self.live_trade,
            mismatch_type="EXTRA TRADE",
            expected=None,
            actual="Unexpected Live execution"
        )
    
    def _analyze_deviation(self, match, time_mismatch, price_mismatch):
        bt = match.backtest_trade
        lt = match.live_trade

        time_diff = abs((lt.trade_time - bt.trade_time).time_threshold())
        if time_diff > self.time_threshold:
            time_mismatch.append(
                TradeMismatch(
                    trade=bt,
                    mismatch_type="TIME MISMATCH",
                    expected=str(bt.trade_time),
                    actual=str(lt.trade_time)
                )
            )
        
        price_diff = abs(lt.price - bt.price)
        if price_diff > price_threshold:
            price_mismatch.append(
                TradeMismatch(
                    trade=bt,
                    mismatch_type="PRICE MISMATCH",
                    expected=str(bt.price),
                    actual=str(lt.price)
                )
            )
        
    def _build_summary(self, matches, missing, extra, time_mismatch, price_mismatch):
        return {
            "total_backtest_trades": len([m for m in matches if m.backtest_trade]),
            "total_live_trades": len([m for m in matches if m.live_trade]),
            "missing_trades": len(missing),
            "extra_trades": len(extra),
            "time_mismatches": len(time_mismatch),
            "price_mismatches": len(price_mismatch),
            "match_rate": round(
                1 - (len(missing) / max(1, len(matches))), 2
            )
        }
