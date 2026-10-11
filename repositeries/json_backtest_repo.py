from __future__ import annotations

import json
from datetime import date, datetime, time, timezone
from pathlib import Path
from typing import List

from config import settings
from models.trade import BacktestRecord


class JsonBacktestRepo:
    """JSON-backed repository for demo and CV presentation use."""

    def __init__(self, data_path: str | None = None):
        base_dir = Path(__file__).resolve().parents[1]
        self.data_path = Path(data_path) if data_path else base_dir / "data" / "demo" / "backtest_trades.json"

    def _load_records(self) -> List[dict]:
        with self.data_path.open("r", encoding="utf-8") as handle:
            records = json.load(handle)
        return records if isinstance(records, list) else []

    def list_strategies(self) -> list[str]:
        strategies = {row.get("strategy") for row in self._load_records() if row.get("strategy")}
        return sorted(strategies)

    def load_trades(self, algoname: str, start_date: date, end_date: date) -> List[BacktestRecord]:
        if start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")

        start_dt = datetime.combine(start_date, time.min, tzinfo=timezone.utc)
        end_dt = datetime.combine(end_date, time.max, tzinfo=timezone.utc)
        trades: List[BacktestRecord] = []

        for row in self._load_records():
            if row.get("strategy") != algoname:
                continue

            try:
                entry_time = self._parse_datetime(row["EntryTime"])
                exit_time = self._parse_datetime(row["ExitTime"])
            except Exception:
                continue

            if not (start_dt <= entry_time <= end_dt or start_dt <= exit_time <= end_dt):
                continue

            trades.append(
                BacktestRecord(
                    EntryTime=entry_time,
                    ExitTime=exit_time,
                    symbol=row["Symbol"],
                    EntryPrice=float(row["EntryPrice"]),
                    ExitPrice=float(row["ExitPrice"]),
                    Quantity=int(row["Quantity"]),
                    PositionStatus=int(row["PositionStatus"]),
                    Pnl=float(row["Pnl"]),
                    ExitType=row["ExitType"],
                    strategy=row["strategy"],
                )
            )

        return trades

    @staticmethod
    def _parse_datetime(value):
        if isinstance(value, str):
            return datetime.fromisoformat(value.replace("Z", "+00:00")).astimezone(timezone.utc)
        if isinstance(value, datetime):
            return value.astimezone(timezone.utc)
        raise ValueError(f"Unsupported datetime value: {value}")
