from datetime import date
from typing import Dict
from pydantic import BaseModel


class Option(BaseModel):
    symbol: str
    tick: str
    expiry: date
    strike: float
    option_type: str
    lot_size: int
    underlying_value: float
    current_price: float
    initial_price: float
    expected_hit: date
    expected_change: float = 0.0
    sold: bool = False


    def change(self) -> float:
        return round((self.current_price - self.initial_price) / self.initial_price, 2)
    
    def update(self, quotes: Dict):
        [quote] = [stock for stock in quotes["stocks"] if stock["metadata"]["identifier"] == self.tick]

        self.current_price = quote["metadata"]["lastPrice"] * self.lot_size
        self.underlying_value = quote["underlyingValue"]

    def expired(self) -> bool:
        today = date.today()
        if today > self.expiry:
            self.expired = True

    def expected_hit_passed(self) -> bool:
        today = date.today()
        if today > self.expected_hit:
            self.expected_hit_passed = True

    def value_near_strike(self) -> bool:
        lower_limit = self.strike * (0.97)
        upper_limit = self.strike * (1.03)
        return lower_limit <= self.underlying_value <= upper_limit
    
    def sell(self) -> bool:
        if self.expected_hit_passed() or self.expired() or self.value_near_strike():
            self.sold = True
        return self.sold
    
