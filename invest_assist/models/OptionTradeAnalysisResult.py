from pydantic import BaseModel


class OptionTradeAnalysisResult(BaseModel):
    total_trades: int
    breakout: int
    change: float
    days: int