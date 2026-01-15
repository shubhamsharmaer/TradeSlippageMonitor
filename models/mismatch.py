from typing import List, Optional
from pydantic import BaseModel
from models.trade import NormalizedTrade

class TradeMismatch(BaseModel):
    lt_trade: NormalizedTrade
    bt_trade: NormalizedTrade
    mismatch_type: str | None
    expected: str | None
    actual: Optional[str]

class TradeMatch(BaseModel):
    lt_trade: NormalizedTrade
    bt_trade: NormalizedTrade
    mismatch_type: str | None

class ExtraTrade(BaseModel):
    trade: NormalizedTrade
    mismatch_type: str | None
    expected: str | None
    actual: Optional[str]


class MissingTrade(BaseModel):
    trade: NormalizedTrade
    mismatch_type: str | None
    expected: str | None
    actual: Optional[str]


class MismatchReport(BaseModel):
    missing_trades: List[MissingTrade]
    extra_trades: List[ExtraTrade]
    matched_trades: List[TradeMatch]
    time_mismatches: List[TradeMismatch]
    price_mismatches: List[TradeMismatch]
    summary: dict