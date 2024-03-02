from typing import List
from trade_analysis import TradeAnalysis


class CumulativeAnalysisResult:
  def __init__(
      self,
      average_return_on_risk: float,
      average_days: int,
      profitable_trades: int,
      loss_making_trades: int,
      average_profit_return: float,
      average_loss_return: float,
      trade_analysis: List[TradeAnalysis]
    ) -> None:
    self.average_return_on_risk = average_return_on_risk
    self.average_days = average_days
    self.profitable_trades = profitable_trades
    self.loss_making_trades = loss_making_trades
    self.average_profit_return = average_profit_return
    self.average_loss_return = average_loss_return
    self.trade_analysis = trade_analysis
