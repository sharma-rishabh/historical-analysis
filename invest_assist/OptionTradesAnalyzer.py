import statistics
from typing import List
from invest_assist.models import OptionTrade, OptionTradeAnalysisResult


class OptionTradeAnalyzer:
    def __init__(self, trades: List[OptionTrade]):
        self.trades = trades

    def analyse(self):
        if len(self.trades) == 0:
            return OptionTradeAnalysisResult(
                days=0, change=0, total_trades=0, breakout=0
            )
        changes = [trade.change for trade in self.trades]
        sorted_changes = sorted(changes)
        seventy_five_percentile = sorted_changes[int(len(sorted_changes) * 0.4)]
        
        return OptionTradeAnalysisResult(
            total_trades=len(self.trades),
            breakout=self.trades[0].breakout,
            change=seventy_five_percentile,
            days=round(sum([trade.days for trade in self.trades]) / len(self.trades))
        )