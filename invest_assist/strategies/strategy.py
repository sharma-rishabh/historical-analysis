from abc import ABC, abstractmethod
from typing import List
from trade import Trade


class Strategy(ABC):
  @abstractmethod
  def execute(self) -> List[Trade]:
    pass

  @abstractmethod
  def get_stop_loss(self) -> float:
    pass

  @abstractmethod
  def breakout(self, today: dict)->bool:
    pass