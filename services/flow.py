from datetime import date
from typing import List, Optional
# Data fetching imports
from repositeries.live_repo import LiveTradeRepo
from repositeries.backtest_repo import BacktestRepo

# Normalization imports
from services.normalizer import normalize_backtest_record, normalize_live_trade_record

# matcher import
from services.matcher import TradeMatchingEngine
from services.detector import MismatchDetector

class TradeMatchingFlowService:
    def __init__(self):
        self.backtest_repo = BacktestRepo()
        self.live_repo = LiveTradeRepo()

        self.matcher = TradeMatchingEngine()
        self.detector = MismatchDetector()

    def reconcile(self, backtest_algo: str, live_algo: str, start_date: date, end_date: date, clientId: Optional[str] = None):
        if clientId:
            return self._recocile_for_client(
                backtest_algo,
                live_algo,
                start_date,
                end_date,
                clientId
            )
        
        # if not client is selected || ALL CLIENTS CASE
        clients = self.live_algo._get_distinct_clients(
            algoname=live_algo,
            start_date=start_date,
            end_date=end_date
        )

        results = {}

        for cid in clients:
            results[cid] = self._recocile_for_client(
                backtest_algo=backtest_algo,
                live_algo=live_algo,
                start_date=start_date,
                end_date=end_date,
                clientId=cid
            )

        return results


    def _reconcile_for_client(
        self,
        backtest_algo: str,
        live_algo: str,
        start_date: date,
        end_date: date,
        clientId: str,
    ):

        # load bt trades
        bt_trades = self.backtest_repo.load_trades(
            algoname=backtest_algo,
            start_date=start_date,
            end_date=end_date
        )

        # load live trades
        lt_trades = self.live_repo.load_trades(
            algoname=live_algo,
            start_date=start_date,
            end_date=end_date,
            clientId=clientId
        )

        # normalize both trades
        normalized_bt_trades = self.normalize_backtest_record(
            records=bt_trades,
            algoname=bt_trades
        )

        normalized_lt_trades = self.normalize_live_trade_record(
            records=lt_trades
        )

        matches = self.matcher.match_trades(
            backtest_trades=normalized_bt_trades,
            live_trades=normalized_lt_trades
        )

        report = self.detector.analyze(matches)

        return report



