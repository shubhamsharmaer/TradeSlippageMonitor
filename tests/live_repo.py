from typing import List
from repositeries.live_repo import LiveTradeRepo
from datetime import date
from services.normalizer import normalize_live_trade_record
if __name__ == "__main__":
    repo = LiveTradeRepo()
    # trades = repo.load_trades(
    #     algoname="DRB_N",
    #     start_date=date(2025, 10, 1),
    #     end_date=date(2025, 10, 31),
    #     clientId=""
    # )
    clients =  repo._get_distinct_clients(
        algoname="DRB_N",
        start_date=date(2025, 10, 1),
        end_date=date(2025, 10, 31)
    )
    print(clients)
    # print(f"Loaded database {len(trades)} trades")
    # trades = normalize_live_trade_record(
    #     records=trades
    # )
    # print(f"Normalized trades: {len(trades)}")