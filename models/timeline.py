from typing import List, Optional, Literal
from pydantic import BaseModel
from models.trade import NormalizedTrade
from datetime import datetime

class TradeEvent(BaseModel):
    time: datetime
    source: Literal['backtest', 'live']
    trade: NormalizedTrade

class TradeTimeline(BaseModel):
    start_date: datetime
    end_date: datetime
    events: List[TradeEvent]