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

  def __eq__(self, value: object) -> bool:
      if not isinstance(value, TradeAnalysis):
          return False
      return (
          self.buying_price == value.buying_price and
          self.selling_price == value.selling_price and
          self.risk == value.risk and
          self.return_on_risk == value.return_on_risk and
          self.days == value.days and
          self.units == value.units and
          self.overall_returns == value.overall_returns
      )
    
