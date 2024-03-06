from functools import reduce
import math
from typing import List
from datetime import date
from pydantic import BaseModel


class Portfolio(BaseModel):
    capital: float
    risk_percent: float
    holdings: List["Holding"]

    def active_stocks(self)->List['Holding']:
        return [holding for holding in self.holdings if not holding.sold]


    def invested(self)->float:
        return reduce(lambda x,y: x + (y.buying_price * y.units), self.active_stocks(), 0)
    
    def current_value(self) -> float:
        return reduce(lambda x,y: x + (y.current_price * y.units), self.active_stocks(), 0)

    def remaining_capital(self) -> float:
        return self.capital - self.invested()
    
    def return_percent(self) -> float:
        total_returns = self.current_value() - self.invested()
        return total_returns/self.invested


    def get_units(self, investment_amount, buying_price, stop_loss)-> int:
        risk_per_unit = buying_price - stop_loss
        risk_amount = self.capital * self.risk_percent
        units_as_per_risk = math.floor(risk_amount / risk_per_unit)
        total_cost = units_as_per_risk * buying_price
        if total_cost <= investment_amount:
            return units_as_per_risk
        return math.floor(investment_amount/buying_price)


    def buy_stock(
            self,
            symbol: str,
            current_price: float,
            buying_price: float,
            stop_loss: float,
            buying_capacity: float,
            strategy: str,
            buying_date: date, 
            hd: 'HistoricalAnalysisResult'
    )-> 'Holding':
        available_investment = self.remaining_capital() * buying_capacity
        units = self.get_units(available_investment, buying_price, stop_loss)

        holding = Holding(
                symbol=symbol,
                units=units,
                current_price=current_price,
                buying_price=buying_price,
                stop_loss=stop_loss,
                strategy=strategy,
                buying_date=buying_date,
                sold=False,
                historical_data=hd
            )   
        if units <= 0:
            return holding
        
        self.holdings.append(holding)
        return holding



class Holding(BaseModel):
    symbol: str
    units: int
    current_price: float
    buying_price: float
    stop_loss: float
    strategy: str
    buying_date: date
    sold: bool
    historical_data: "HistoricalAnalysisResult"


class HistoricalAnalysisResult(BaseModel):
    returns: float
    days_per_return: int
    total_trades: int
    winning_percentage: float
