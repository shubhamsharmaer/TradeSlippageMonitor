from typing import List
from repositeries.live_repo import LiveTradeRepo
from repositeries.backtest_repo import BacktestRepo
from datetime import date
from services.normalizer import normalize_live_trade_record, normalize_backtest_record
from services.matcher import TradeMatchingEngine
from helpers.csv_saver import save_to_csv_pd
from services.detector import MismatchDetector
from helpers.matchresult_csv import match_results_to_rows



if __name__ == "__main__":
    repo = LiveTradeRepo()
    bt_repo = BacktestRepo()
    trade_repo = TradeMatchingEngine()
    detector_repo = MismatchDetector()

    bt_trades = bt_repo.load_trades(
        algoname="DRB_N_oct24",
        start_date=date(2025, 10, 1),
        end_date=date(2025, 10, 31)
    )
    # save_to_csv_pd(bt_trades, "bt_trades_from_db.csv")
    norm_bt_trades = normalize_backtest_record(
        records=bt_trades,
        # algoname="DRB_N_oct24",
    )
    save_to_csv_pd(norm_bt_trades, "norm_bt_trades.csv")
    lt_trades = repo.load_trades(
        algoname="DRB_N",
        start_date=date(2025, 10, 1),
        end_date=date(2025, 10, 31),
        clientId="D7730028"
    )
    # save_to_csv_pd(lt_trades, "lt_trades.csv")
    norm_lt_trades = normalize_live_trade_record(
        records=lt_trades
    )
    save_to_csv_pd(norm_lt_trades, "norm_lt_trades.csv")

    print(f"---------------------TRADES LOADED--------------------------")
    print(f"Total Backtest trades: {len(bt_trades)}")
    print(f"Total Live trades: {len(lt_trades)}")
    print(f"-------------------------------------------------------------")
    print(f"---------------------NORMALIZED TRADES LOADED--------------------------")
    print(f"Normalized Total Backtest trades: {len(norm_bt_trades)}")
    print(f"Normalized Total Live trades: {len(norm_lt_trades)}")

    matcher = trade_repo.match_trades(
        backtest_trades=norm_bt_trades,
        live_trades=norm_lt_trades
    )

    results = detector_repo.analyze(matcher)
    df = match_results_to_rows(matcher)

    # ---- matched ----
    matched_df = df[df["status"] == "MATCHED"]
    matched_df.to_csv("matched_trades.csv", index=False)

    # ---- unmatched (missing + extra) ----
    unmatched_df = df[df["status"] != "MATCHED"]
    unmatched_df.to_csv("unmatched_trades.csv", index=False)

    print("✅ CSV exports created:")
    print(f"Matched trades: {len(matched_df)}")
    print(f"Unmatched trades: {len(unmatched_df)}")
