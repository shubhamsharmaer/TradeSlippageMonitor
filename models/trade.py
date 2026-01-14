from pydantic import BaseModel, Field
from typing import Optional, Literal
from datetime import datetime, date

class NormalizedTrade(BaseModel):
    """A normalized representation of a trade event."""

    # trade_id: Optional[str] = None
    source: Literal["backtest", "live"]
    
    # Core identification
    algoname: str
    symbol: str
    clientID: Optional[str] = None

    # Trade details
    trade_type: Literal["BUY", "SELL"]  # Entry=SELL, Exit=BUY for shorts
    price: float # Trade execution price
    quantity: int

    # Matching metadata
    trade_time: Optional[datetime] 
    # normalized_symbol: str 

    # raw_data: dict  # Store original record for debugging

class BacktestRecord(BaseModel):
    """Representation of a backtest trade record."""

    EntryTime: datetime
    ExitTime: datetime
    symbol: str
    EntryPrice: float
    ExitPrice: float
    Quantity: int
    PositionStatus: int  # -1 for short, 1 for long
    Pnl: float
    ExitType: str

class LiveTradeRecord(BaseModel):
    """Live trade MongoDB record"""

    id: Optional[str] = Field(default=None, alias="_id")
    quantity: int
    algoname: str
    symbol: str
    buy_sell: Literal["BUY", "SELL"]
    orderStatus: str
    OrderAverageTradedPrice: str
    clientID: str
    orderSentTime: float
    normalized_quantity: Optional[int] = 1
    # trade_time: datetime
 