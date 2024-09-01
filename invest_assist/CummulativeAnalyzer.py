from typing import List

from invest_assist.models import CumulativeAnalysisResult, HighLowTradesAnalysisResult


class CumulativeAnalyzer:
    def __init__(self, tradeAnalysisResults: List[HighLowTradesAnalysisResult], type: str) -> None:
        self.tradeAnalysisResults = tradeAnalysisResults
        self.type = type

    def analyse(self) -> CumulativeAnalysisResult:
        valid_trades = [trade for trade in self.tradeAnalysisResults if trade.total_trades >= 20]

        if len(valid_trades) == 0:
            return CumulativeAnalysisResult(type= self.type)
        total_analysis = len(valid_trades) 
        total_trades = sum([trade.total_trades for trade in valid_trades])
        profitable_trades = sum([trade.profitable_trades for trade in valid_trades])
        days = sum([trade.days for trade in valid_trades])
        returns = sum([trade.returns for trade in valid_trades])
        returns_on_risk = sum([trade.returns_on_risk for trade in valid_trades])
        risk_on_investment = sum([trade.risk_on_investment for trade in valid_trades])

        return CumulativeAnalysisResult(
            type= self.type,
            total_trades=total_trades,
            profitable_trades=round(profitable_trades / total_analysis, 2),
            days=round(days / total_analysis, 2),
            returns=round(returns / total_analysis, 2),
            returns_on_risk=round(returns_on_risk / total_analysis, 2),
            risk_on_investment=round(risk_on_investment / total_analysis, 2),
        )
        

        

