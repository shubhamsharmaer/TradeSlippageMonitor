from repositeries.backtest_repo import BacktestRepo
from models.trade import BacktestRecord
from services.normalizer import normalize_backtest_record
from datetime import datetime, date
if __name__ == "__main__":
    repo = BacktestRepo()
    
    trades = repo.load_trades(
        algoname="DRB_N_oct24",
        start_date=date(2025, 10, 1),
        end_date=date(2025, 10, 31)
    )
    
    print(f"Loaded database {len(trades)} trades")
        
    trades = normalize_backtest_record(
        records=trades,
        algoname="DRB_N_oct24",
    )
    # for t in trades[:1]:
    #     print(t)
    print(f"Loaded Normalized: {len(trades)} trades")