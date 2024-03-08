from functools import reduce
import math
from typing import List
from datetime import date
from pydantic import BaseModel


class Portfolio(BaseModel):
    current_id: int = 0
    capital: float
    risk_percent: float
    holdings: List["Holding"]

    def find_by_id(self, id: int) -> 'Holding':
        return [holding for holding in self.active_stocks() if holding.id == id][0]
    
    def find_by_symbol(self, symbol: str) -> List['Holding']:
        return [holding for holding in self.active_stocks() if holding.symbol == symbol]
    
    def sell_by_symbol(self, symbol: str, selling_price: float | None) -> float:
        holdings_to_sell = self.find_by_symbol(symbol)
        for holding in holdings_to_sell:
            sold_for = holding.sell(selling_price)
        return sold_for
    
    def sell_by_id(self, id: int, selling_price: float | None) -> float:
        holding_to_sell = self.find_by_id(id)
        return holding_to_sell.sell(selling_price)

    def sell_holdings(self, id: int|None, symbol: str|None, selling_price: float|None) -> float:
        if id:
            return self.sell_by_id(id, selling_price)
        
        return self.sell_by_symbol(symbol, selling_price)

    def get_next_id(self):
        self.current_id += 1
        return self.current_id
    

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

        holding.id = self.get_next_id()        
        self.holdings.append(holding)
        return holding
    


class Holding(BaseModel):
    id: int | None = None
    symbol: str
    units: int
    current_price: float
    buying_price: float
    stop_loss: float
    strategy: str
    buying_date: date
    sold: bool
    historical_data: "HistoricalAnalysisResult"
    selling_price: float | None = None

    def update_stop_loss(self, new_stop_loss: float)-> bool:
        is_stop_loss_changed = self.stop_loss != new_stop_loss
        self.stop_loss = new_stop_loss
        return is_stop_loss_changed 
    
    def update_current_price(self, new_price: float)->bool:
        self.current_price = new_price
        return True
    
    def sell(self, selling_price: float | None) -> float:
        self.selling_price = selling_price if selling_price else self.stop_loss
        self.sold = True
        return self.selling_price

class HistoricalAnalysisResult(BaseModel):
    returns: float
    days_per_return: int
    total_trades: int
    winning_percentage: float
