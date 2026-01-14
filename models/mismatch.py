from typing import List, Optional
from pydantic import BaseModel
from models.trade import NormalizedTrade

class TradeMismatch(BaseModel):
    trade: NormalizedTrade
    mismatch_type: str
    expected: str
    actual: Optional[str]


class MismatchReport(BaseModel):
    missing_trades: List[TradeMismatch]
    extra_trades: List[TradeMismatch]
    time_mismatches: List[TradeMismatch]
    price_mismatches: List[TradeMismatch]
    summary: dict