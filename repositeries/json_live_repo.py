from __future__ import annotations

import json
from datetime import date, datetime, timezone
from pathlib import Path
from typing import List, Optional

from models.trade import LiveTradeRecord


class JsonLiveRepo:
    """JSON-backed repository for demo and CV presentation use."""

    def __init__(self, data_path: str | None = None):
        base_dir = Path(__file__).resolve().parents[1]
        self.data_path = Path(data_path) if data_path else base_dir / "data" / "demo" / "live_trades.json"

    def _load_records(self) -> List[dict]:
        with self.data_path.open("r", encoding="utf-8") as handle:
            records = json.load(handle)
        return records if isinstance(records, list) else []

    def list_algonames(self) -> List[str]:
        algos = {row.get("algoname") for row in self._load_records() if row.get("algoname")}
        return sorted(algos)

    def list_clients(self) -> List[str]:
        clients = {row.get("clientID") for row in self._load_records() if row.get("clientID")}
        return sorted(clients)

    def list_brokers(self) -> List[str]:
        brokers = {row.get("broker") for row in self._load_records() if row.get("broker")}
        return sorted(brokers)

    def _get_distinct_clients(self, algoname: str, start_date: date, end_date: date) -> List[str]:
        start_ts = datetime.combine(start_date, datetime.min.time()).timestamp()
        end_ts = datetime.combine(end_date, datetime.max.time()).timestamp()
        clients = set()

        for row in self._load_records():
            if row.get("algoname") != algoname:
                continue
            order_sent = float(row.get("orderSentTime", 0))
            if start_ts <= order_sent <= end_ts:
                client_id = row.get("clientID")
                if client_id:
                    clients.add(client_id)

        return sorted(clients)

    def load_trades(
        self,
        algoname: str,
        start_date: date,
        end_date: date,
        clientId: Optional[str] = None,
        broker: Optional[str] = None,
    ) -> List[LiveTradeRecord]:
        if start_date > end_date:
            raise ValueError("start_date must be before or equal to end_date")

        start_ts = datetime.combine(start_date, datetime.min.time()).timestamp()
        end_ts = datetime.combine(end_date, datetime.max.time()).timestamp()
        trades: List[LiveTradeRecord] = []

        for row in self._load_records():
            if row.get("algoname") != algoname:
                continue
            if clientId and row.get("clientID") != clientId:
                continue
            if broker and row.get("broker") != broker:
                continue

            order_sent = float(row.get("orderSentTime", 0))
            if not (start_ts <= order_sent <= end_ts):
                continue

            trades.append(
                LiveTradeRecord(
                    quantity=int(row["quantity"]),
                    algoname=row["algoname"],
                    symbol=row["symbol"],
                    buy_sell=row["buy_sell"],
                    orderStatus=row["orderStatus"],
                    OrderAverageTradedPrice=str(row["OrderAverageTradedPrice"]),
                    clientID=row["clientID"],
                    orderSentTime=order_sent,
                    broker=row["broker"],
                )
            )

        return trades
