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

# time line maker 
from services.timeline_maker import TimelineMakerService
from helpers.timeline_csv import timeline_rows
from helpers.matchresult_csv import results_to_csv

class TradeMatchingFlowService:
    def __init__(self):
        self.backtest_repo = BacktestRepo()
        self.live_repo = LiveTradeRepo()

        self.matcher = TradeMatchingEngine()
        self.detector = MismatchDetector()

        self.timeline = TimelineMakerService()

    def reconcile(self, backtest_algo: str, live_algo: str, start_date: date, end_date: date, clientId: Optional[str] = None):
        if clientId:
            return self._reconcile_for_client(
                backtest_algo,
                live_algo,
                start_date,
                end_date,
                clientId
            )
        
        # if not client is selected || ALL CLIENTS CASE
        clients = self.live_repo._get_distinct_clients(
            algoname=live_algo,
            start_date=start_date,
            end_date=end_date
        )

        results = {}

        for cid in clients:
            # print(f"Processing Client: {cid}")
            results[cid] = self._reconcile_for_client(
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
        normalized_bt_trades = normalize_backtest_record(
            records=bt_trades,
            # algoname=bt_trades.algoname
        )

        normalized_lt_trades = normalize_live_trade_record(
            records=lt_trades
        )

        timeline = self.timeline.timeline_builder(
            backtest_trades=normalized_bt_trades,
            live_trades=normalized_lt_trades,
            start_date=start_date,
            end_date=end_date
        )
        df = timeline_rows([timeline])
        df.to_csv("trade_timeline.csv", index=False)


        # matches = self.matcher.match_trades(
        #     backtest_trades=normalized_bt_trades,
        #     live_trades=normalized_lt_trades
        # )

        matches = self.matcher.match_trades(timeline)

        df = results_to_csv(timeline=timeline, match_results=matches)
        df.to_csv('matches_results.csv', index=False)

        report = self.detector.analyze(matches, timeline)

        return report



