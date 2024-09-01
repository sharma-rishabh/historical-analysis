from typing import List
from invest_assist.models import HighLowTrade, HighLowTradesAnalysisResult


class HighLowAnalyzer:
    def __init__(self, data: List[HighLowTrade]):
        self.data = data

    def analyze(self) -> HighLowTradesAnalysisResult:
        total_trades = len(self.data)

        if total_trades == 0:
            return HighLowTradesAnalysisResult()

        profitable_trades = 0
        total_returns = 0
        total_returns_on_risk = 0
        total_risk_on_investment = 0
        total_days = 0


        for trade in self.data:
            profitable_trades += 1 if trade.returns() > 0 else 0
            total_returns += trade.returns()
            total_returns_on_risk += trade.returns_on_risk()
            total_risk_on_investment += trade.risk_on_investment()
            total_days += trade.days()


        return HighLowTradesAnalysisResult(
            total_trades=total_trades,
            profitable_trades=round(profitable_trades / total_trades, 2),
            days=round(total_days / total_trades, 2),
            returns=round(total_returns / total_trades, 2),
            returns_on_risk=round(total_returns_on_risk / total_trades, 2),
            risk_on_investment=round(total_risk_on_investment / total_trades, 2),
        )
