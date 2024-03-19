import pandas as pd
import math
from typing import List, Type
from jugaad_data.nse import stock_df
from invest_assist.trade import Trade
from datetime import timedelta, date
from invest_assist.trade_analysis import TradeAnalysis
from functools import reduce
from invest_assist.models import Portfolio, HistoricalAnalysisResult
from invest_assist.strategies import Strategy

class Analyzer:
    def __init__(self, symbol: str, portfolio: Portfolio, strategy: Type[Strategy], days: int) -> None:
        self.symbol = symbol
        self.portfolio = portfolio
        self.strategy = strategy
        self.days = days

    def get_historical_data(self) -> pd.DataFrame:
        today = date.today()
        ten_years_ago = today - timedelta(days=self.days)
        df = stock_df(symbol=self.symbol, from_date=ten_years_ago, to_date=today, series="EQ")

        df = df.drop_duplicates()
        return df

    def get_trades(self):
        historical_data = self.get_historical_data()
        return self.strategy(historical_data).execute()

    def risk(self) -> float:
        return self.portfolio.capital * self.portfolio.risk_percent

    def overall_return(self, units: int, buying_price: float, selling_price: float) -> float:
        return round((units * selling_price) - (units * buying_price), 2)

    def get_units(self, trade: Trade) -> int:
        risk_per_unit = trade.buy_price - trade.initial_stop_less
        units_as_per_risk = math.floor(self.risk() / risk_per_unit)
        total_investment = units_as_per_risk * trade.buy_price

        if total_investment < self.portfolio.capital:
            return units_as_per_risk

        return math.floor(self.portfolio.capital / trade.buy_price)

    def get_trade_analysis(self, trade: Trade) -> TradeAnalysis:
        units = self.get_units(trade)
        risk_per_unit = trade.buy_price - trade.initial_stop_less
        risk = units * risk_per_unit

        if risk == 0:
            return TradeAnalysis(0,0,0,0,0,0,0)

        overall_returns = self.overall_return(
            units,
            trade.buy_price,
            trade.selling_price
        )
        
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

    def avg_return(self, trade_analysis: List[TradeAnalysis]) -> float:
        return round(reduce(lambda x, y: x + y.return_on_risk, trade_analysis,0) / len(trade_analysis), 2)
    
    def avg_days(self, trade_analysis: List[TradeAnalysis]) -> int:
        return math.ceil(reduce(lambda x, y: x + y.days, trade_analysis, 0) / len(trade_analysis))
    
    def profitable_trades(self,trade_analysis: List[TradeAnalysis]) -> List[TradeAnalysis]:
        return [trade for trade in trade_analysis if trade.return_on_risk >= 0]
    
    def analyse(self) -> HistoricalAnalysisResult:
        trades = self.get_trades()
        trade_analysis =  [self.get_trade_analysis(trade) for trade in trades]
        avg_rate_of_return = self.avg_return(trade_analysis)
        avg_days = self.avg_days(trade_analysis)
        profitable_trades = self.profitable_trades(trade_analysis)
        profit_percent = round(len(profitable_trades) / len(trade_analysis), 2)

        return HistoricalAnalysisResult(
            returns=avg_rate_of_return,
            days_per_return=avg_days,
            winning_percentage=profit_percent,
            total_trades=len(trade_analysis)
        )
