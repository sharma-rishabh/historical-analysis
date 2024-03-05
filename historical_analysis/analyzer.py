from datetime import timedelta
import math
from typing import List
from cumulative_analysis_result import CumulativeAnalysisResult
from trade import Trade
from risk_profile import RiskProfile
from trade_analysis import TradeAnalysis
from functools import reduce

class Analyzer:
    def __init__(self, trades: List[Trade], profile: RiskProfile) -> None:
        self.trades = trades
        self.profile = profile

    def get_units(self, trade: Trade) -> int:
        risk_per_unit = trade.buy_price - trade.initial_stop_less
        units_as_per_risk = math.floor(self.profile.risk / risk_per_unit)
        total_investment = units_as_per_risk * trade.buy_price
        if total_investment < self.profile.capital:
            return units_as_per_risk

        return math.floor(self.profile.capital / trade.buy_price)

    def get_trade_analysis(self, trade: Trade) -> TradeAnalysis:
        units = self.get_units(trade)
        risk_per_unit = trade.buy_price - trade.initial_stop_less
        risk = units * risk_per_unit

        if risk == 0:
            return TradeAnalysis(0,0,0,0,0,0,0)

        overall_returns = round((units * trade.selling_price) - (units * trade.buy_price),2)
        return_on_risk = round(overall_returns / risk, 2)

        time_diff = trade.selling_date - trade.start_date
        return TradeAnalysis(
            buying_price=trade.buy_price,
            selling_price=trade.selling_price,
            risk=risk,
            return_on_risk=return_on_risk,
            days=time_diff.days,
            units=units,
            overall_returns=overall_returns
        )

    def avg_return(self, trade_analysis: List[TradeAnalysis]):
        return round(reduce(lambda x, y: x + y.return_on_risk, trade_analysis,0) / len(trade_analysis), 2)

    def analyse(self) -> CumulativeAnalysisResult:
        trade_analysis =  [self.get_trade_analysis(trade) for trade in self.trades]

        avg_rate_of_return = self.avg_return(trade_analysis)

        avg_days = math.ceil(reduce(lambda x, y: x + y.days, trade_analysis, 0) / len(trade_analysis))

        profitable_trades = [trade for trade in trade_analysis if trade.return_on_risk >= 0]


        average_return_on_profit = self.avg_return(profitable_trades)

        profit_percent = round(len(profitable_trades) / len(trade_analysis), 2)

        return CumulativeAnalysisResult(
            avg_rate_of_return,
            avg_days,
            profit_percent,
            average_return_on_profit,
            trade_analysis
        )
