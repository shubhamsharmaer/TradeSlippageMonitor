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
from helpers.matchresult_csv import results_to_csv, results_to_csv_split
import pandas as pd

class NoBacktestTrades(Exception):
    pass
class NoLiveTrades(Exception):
    pass

class TradeMatchingFlowService:
    def __init__(self, live_repo: LiveTradeRepo | None = None, backtest_repo: BacktestRepo | None = None):
        self.backtest_repo = backtest_repo or BacktestRepo()
        self.live_repo = live_repo or LiveTradeRepo()

        self.matcher = TradeMatchingEngine()
        self.detector = MismatchDetector()

        self.timeline = TimelineMakerService()

    def reconcile(
            self, 
            backtest_algo: str, 
            live_algo: str, 
            start_date: date, 
            end_date: date, 
            price_tolerance: float,
            clientId: Optional[str] = None, 
            min_price_for_hedge: Optional[float] = None,
            check_qnt: Optional[bool] = False,
            broker: str = None,
        ):
        if clientId:
            return self._reconcile_for_client(
                backtest_algo,
                live_algo,
                start_date,
                end_date,
                price_tolerance=price_tolerance,
                clientId=clientId,
                min_price_for_hedge=min_price_for_hedge,
                check_qnt=check_qnt,
                broker=broker
            )
        
        # if not client is selected || ALL CLIENTS CASE
        clients = self.live_repo._get_distinct_clients(
            algoname=live_algo,
            start_date=start_date,
            end_date=end_date,
        )

        results = {}

        for cid in clients:
            # print(f"Processing Client: {cid}")
            results[cid] = self._reconcile_for_client(
                backtest_algo=backtest_algo,
                live_algo=live_algo,
                start_date=start_date,
                end_date=end_date,
                price_tolerance=price_tolerance,
                clientId=cid,
                min_price_for_hedge=min_price_for_hedge,
                check_qnt=check_qnt,
                broker=broker,
            )

        return results


    def _reconcile_for_client(
        self,
        backtest_algo: str,
        live_algo: str,
        start_date: date,
        end_date: date,
        price_tolerance: float,
        clientId: str,
        min_price_for_hedge: float,
        check_qnt: bool,
        broker: str,
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
            clientId=clientId,
            broker=broker
        )

        if len(bt_trades) == 0:
            raise NoBacktestTrades("no backtest trades found for this time period")

        elif len(lt_trades) == 0:
            raise NoLiveTrades("no live trades found for this time period")
            
        # normalize both trades
        normalized_bt_trades = normalize_backtest_record(
            records=bt_trades,
        )

        normalized_lt_trades = normalize_live_trade_record(
            records=lt_trades,
            min_price_for_hedge = min_price_for_hedge
        )

        # df = pd.DataFrame(normalized_lt_trades)
        # df.to_csv('hedge.csv')

        timeline = self.timeline.timeline_builder(
            backtest_trades=normalized_bt_trades,
            live_trades=normalized_lt_trades,
            start_date=start_date,
            end_date=end_date
        )
        # df = timeline_rows([timeline])
        # df.to_csv("trade_timeline.csv", index=False)

        matches = self.matcher.match_trades(timeline, price_tolerance, check_qnt)

        # df = results_to_csv(timeline=timeline, match_results=matches)
        # df.to_csv('matches_results.csv', index=False)
        # df = results_to_csv_split(match_results=matches)
        # df.to_csv(f'{live_algo}_split_results.csv', index=False)

        report = self.detector.analyze(matches, timeline)

        return report



