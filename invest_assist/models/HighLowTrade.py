from datetime import datetime
from pydantic import BaseModel


class HighLowTrade(BaseModel):
    buy_price: float
    start_date: datetime
    initial_stop_loss: float
    stop_loss: float
    sell_price: float | None = None
    end_date: datetime | None = None

    def update_stop_loss(self, new_stop_loss: float):
        self.stop_loss = new_stop_loss

    def sell(self, end_date: str):
        self.sell_price = self.stop_loss
        self.end_date = end_date

    def returns(self):
        return (self.sell_price - self.buy_price) / self.buy_price
    
    def returns_on_risk(self):
        if self.risk() == 0:
            return 0
        return self.returns() / self.risk()
    
    def risk_on_investment(self):
        return self.risk()

    def risk(self):
        return (self.buy_price - self.initial_stop_loss) / self.buy_price
    
    def days(self):
        return (self.end_date - self.start_date).days