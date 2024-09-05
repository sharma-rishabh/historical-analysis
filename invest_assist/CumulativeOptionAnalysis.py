from typing import List

from invest_assist.models import OptionTradeAnalysisResult


class CumulativeOptionAnalysis:
    def __init__(self, analysis: List[OptionTradeAnalysisResult]) -> None:
        self.analysis = analysis

    def analyse(self) -> OptionTradeAnalysisResult:
        valid_analysis = [analysis for analysis in self.analysis if analysis.total_trades >= 20]

        if len(valid_analysis) == 0:
            return OptionTradeAnalysisResult(
                days=0, change=0, total_trades=0, breakout=0
            )
        
        return max(valid_analysis, key=lambda x: x.change)
        