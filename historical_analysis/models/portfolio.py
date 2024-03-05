from typing import List
from datetime import date
from pydantic import BaseModel


class Portfolio(BaseModel):
  capital: float
  invested: float
  current_value: float
  return_percent: float
  risk_percent: float
  holdings: List['Holding']


class Holding(BaseModel):
  symbol: str
  units: int
  buying_price: float
  stop_loss: float
  strategy: str
  buying_date: date
  historical_data: 'HistoricalData'


class HistoricalData(BaseModel):
  returns: float
  days_per_return: int
  total_trades: int
  winning_percentage: float