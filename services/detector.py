from typing import List
from models.mismatch import (
    TradeMismatch, MismatchReport, 
    TradeMatch, MissingTrade, ExtraTrade)
from models.timeline import TradeTimeline
# from services.matcher import MatchResult
from services.matcher import (
    MatchResult,
    MissingLiveTrade,
    ExtraLiveTrade,
    MatchOutcome
)
from datetime import date, timedelta
from logger_setup import logger
import traceback


class MismatchDetector:

    def analyze(self, matches: List[MatchResult], timeline_trades) -> MismatchReport:
        try:
            logger.info("🔃 Report Making Started")

            matched = []
            missing = [] # in backtest but not in live
            extra = []  # in live but not in backtest
            time_mismatch = []
            price_mismatch = []

            timeline_trades = timeline_trades
            
            logger.info("Loop in matches from matcher started")
            for m in matches:
                if m.backtest_trade and not m.live_trade:
                    missing.append(self._missing_trade(m))

                if not m.backtest_trade and m.live_trade:
                    extra.append(self._extra_trade(m))
                
                if m.matched:
                    matched.append(self._matched_trade(m))

                if m.time_mismatch:
                        time_mismatch.append(self._time_mismatch(m))

                if m.price_mismatch:
                    price_mismatch.append(self._price_mismatch(m))
            
            summary = self._build_summary(matches, missing, extra, matched, price_mismatch)

            logger.info("✅ Summary Generated")
            logger.info("✅ Report Generated")
            
            return MismatchReport(
                timeline_trades=timeline_trades,
                extra_trades=extra,
                missing_trades=missing,
                matched_trades=matched,
                time_mismatches=time_mismatch,
                price_mismatches=price_mismatch,
                summary=summary
            )
        except Exception as e:
            logger.error("❌ Something went wrong analyze function of detector service")
            return (traceback.format_exc())

    def _missing_trade(self, match: MatchResult) -> MissingTrade:
        return MissingTrade(
            trade=match.backtest_trade,
            mismatch_type="MISSING TRADE",
            expected="Live Execution",
            actual=None
        )

    def _extra_trade(self, match: MatchResult) -> ExtraTrade:
        return ExtraTrade(
            trade=match.live_trade,
            mismatch_type="EXTRA TRADE",
            expected=None,
            actual="Unexpected Live execution"
        )
    
    def _matched_trade(self, match: MatchResult) -> TradeMatch:
        return TradeMatch(
            bt_trade=match.backtest_trade,
            lt_trade=match.live_trade,
            mismatch_type=match.reason
        )

    def _time_mismatch(self, match: MatchResult) -> TradeMismatch:
        return TradeMismatch(
            lt_trade=match.live_trade,
            bt_trade=match.backtest_trade,
            mismatch_type="TIME MISMATCH",
            expected=str(match.backtest_trade.trade_time),
            actual=str(match.live_trade.trade_time)
        )
    
    def _price_mismatch(self, match: MatchResult) -> TradeMismatch:
        return TradeMismatch(
            lt_trade=match.live_trade,
            bt_trade=match.backtest_trade,
            mismatch_type="PRICE MISMATCH",
            expected=str(match.backtest_trade.price),
            actual=str(match.live_trade.price)
        )
    
    def _build_summary(self, matches, missing, extra, matched, price_m):
        bt_count = len([m for m in matches if m.backtest_trade])

        return {
            "total_backtest_trades": bt_count,
            "total_live_trades": len([m for m in matches if m.live_trade]),
            "matched_trades": len(matched),
            "missing_trades": len(missing),
            "extra_trades": len(extra),
            # "time_mismatches": len(time_m),
            "price_mismatches": len(price_m),
            "match_rate": round(len(matched) / max(1, bt_count), 2)
        }
