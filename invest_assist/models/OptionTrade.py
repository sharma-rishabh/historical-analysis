from datetime import datetime
from pydantic import BaseModel


class OptionTrade(BaseModel):
    breakout: int
    start_price: float
    change: float
    days: int
    current_limit: float
    start_date: datetime

    def update_change(self, new_limit: float, date: datetime):
        self.change = round((new_limit - self.start_price) / self.start_price,2)
        self.current_limit = new_limit
        self.days = (date - self.start_date).days