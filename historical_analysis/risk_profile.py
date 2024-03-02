class RiskProfile:
  def __init__(self, capital: int, risk_percentage: float) -> None:
    self.capital = capital
    self.risk_percentage = risk_percentage
    self.risk = capital * risk_percentage
