from pydantic import BaseModel


class HighLowTradesAnalysisResult(BaseModel):
    total_trades: int = 0
    profitable_trades: float = 0
    days: float = 0
    returns: float = 0
    returns_on_risk: float = 0
    risk_on_investment: float = 0