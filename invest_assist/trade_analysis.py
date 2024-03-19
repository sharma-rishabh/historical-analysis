from datetime import datetime
class TradeAnalysis:
  def __init__(
        self,
        buying_price: int,
        selling_price: int,
        risk: int,
        return_on_risk: float,
        days: int,
        units: int,
        overall_returns: float
    ) -> None:
        self.buying_price = buying_price 
        self.selling_price = selling_price 
        self.risk = risk 
        self.return_on_risk = return_on_risk 
        self.days = days 
        self.units = units 
        self.overall_returns = overall_returns

    
