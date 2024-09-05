from datetime import date
from typing import List
from pydantic import BaseModel

from invest_assist.models import Option


class OptionPortfolio(BaseModel):
    date: date
    capital: float = 0.0
    cash_input: float = 0.0
    risk: float = 0.1
    options: List[Option]

    def active_options(self) -> List[Option]:
        return [option for option in self.options if not option.sold]

    def add_cash(self, cash: float):
        self.cash_input += cash
        self.capital += cash

    def add_option(self, option: Option):
        self.options.append(option)
        self.capital -= option.initial_price

    def add_options(self, options: List[Option]):
        for option in options:
            if option.initial_price <= self.capital:
                self.add_option(option)

    def remaining_capital(self) -> float:
        return self.capital
    
    def overall_returns(self) -> float:
        return round(((self.current_value() + self.remaining_capital()) - self.cash_input) / self.cash_input, 2)

    def total_invested(self) -> float:
        return sum([option.initial_price for option in self.active_options()])

    def current_value(self)-> float:
        return sum([option.current_price for option in self.active_options()])

    def change(self) -> float:
        return round((self.current_value() - self.total_invested()) / self.total_invested(), 2)

    def update(self, quotes):
        for option in self.active_options():
            option.update(quotes[option.symbol])

    def sell_options(self):
        for option in self.active_options():
            if option.sell():
                self.capital += option.current_price
            

