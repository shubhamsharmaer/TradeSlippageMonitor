from datetime import datetime, date, time, timezone, timedelta
from typing import Optional, Literal, List
from models.trade import NormalizedTrade, BacktestRecord, LiveTradeRecord
from helpers.date_time_combine import combine_date_and_time
from helpers.timestamp_to_datetime import epoch_to_datetime
IST = timezone(timedelta(hours=5, minutes=30))
from helpers.quantity_norm import NormalizedQuantity
from logger_setup import logger

normalized_quantity_repo = NormalizedQuantity()

def normalize_backtest_record(
    records: List[BacktestRecord],
    # algoname: str,
) -> List[NormalizedTrade]:
    """Convert BacktestRecord to NormalizedTrade"""
    try:
        normalized: List[NormalizedTrade] = []
        logger.info(f"🔃 Normalizing {len(records)} backtest trades")

        for record in records:
            entry_dt = record.EntryTime.astimezone(timezone.utc)
            exit_dt = record.ExitTime.astimezone(timezone.utc)

            # print(type(entry_dt), entry_dt)
            # print(type(exit_dt), exit_dt)

            if record.PositionStatus == -1:
                entry_type, exist_type = "SELL", "BUY"
            elif record.PositionStatus == 1:
                entry_type, exist_type = "BUY", "SELL"
            else:
                raise ValueError(f"Invalid PositionStatus: {record.PositionStatus}")
            

            # Entry trade
            normalized.append(
                NormalizedTrade(
                    trade_id=None,
                    source="backtest",
                    algoname=record.strategy,
                    symbol=record.symbol,
                    clientID=None,
                    trade_type=entry_type,
                    price=record.EntryPrice,
                    quantity=record.Quantity,
                    trade_time=entry_dt,
                    raw_data=record.dict(),
                )
            )

            # Exit trade
            normalized.append(
                NormalizedTrade(
                    trade_id=None,
                    source="backtest",
                    algoname=record.strategy,
                    symbol=record.symbol,
                    clientID=None,
                    trade_type=exist_type,
                    price=record.ExitPrice,
                    quantity=record.Quantity,
                    trade_time=exit_dt,
                    raw_data=record.dict(),
                )
            )
            # print(f"total trades count: {len(normalized)}")
        logger.info(f"✅ All Backtest Trades Normalized")
        return normalized
    except Exception as e:
        logger.error("❌ Something went wrong in backtesting normalization")

def normalize_live_trade_record(
    records: List[LiveTradeRecord]
) -> List[NormalizedTrade]:
    """Convert LiveTradeRecord to NormalizedTrade"""
    # try:

    normalized: List[NormalizedTrade] = []
    logger.info(f"🔃 Normalizing {len(records)} live trades")

    for record in records:
            # converted_trade_time = epoch_to_datetime(record.orderSentTime)
            trade_time = datetime.fromtimestamp(
                record.orderSentTime,
                tz=timezone.utc
                )
            
            # trade_time_naive = trade_time.replace(tzinfo=None)
            trade_time_rounded = trade_time.replace(microsecond=0, second=0)
            normalized_quantity = normalized_quantity_repo.get_normalized_quantity(
                algoname = record.algoname,
                clientID= record.clientID,
                original_quantity= record.quantity
            )
            
            normalized_trade = NormalizedTrade(
                trade_id=record.id,
                source="live",
                algoname=record.algoname,
                symbol=record.symbol,
                clientID=record.clientID,
                trade_type=record.buy_sell,
                price=float(record.OrderAverageTradedPrice),
                quantity=normalized_quantity,
                trade_time=trade_time_rounded,
                # raw_data=record.dict(by_alias=True),
            )

            normalized.append(normalized_trade)
    logger.info(f"✅ All Live Trades Normalized")
    return normalized
    # except Exception as e:
    #     logger.exception("❌ Something went wrong in live normalization")
    #     raise
