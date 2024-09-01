import pandas as pd
from invest_assist.models import HighLowTrade
from invest_assist.trade import Trade
from typing import List
from .strategy import Strategy



class FindHighLow(Strategy):
    def __init__(self, df: pd.DataFrame, high: int, low: int):
        self.df = df.copy()
        self.high = high
        self.low = low


    def preprocess(self):
        self.df = self.df[::-1].reset_index(drop=True)
        self.df = self.df.drop_duplicates()

        self.df["CURRENT_HIGH"] = self.df["HIGH"].rolling(window=self.high).max()
        self.df["CURRENT_LOW"] = self.df["LOW"].rolling(window=self.low).min()
        self.df.dropna(how="any", inplace=True)
        self.df = self.df.reset_index()

    def can_buy(self, row: pd.Series) -> bool:
        return row["HIGH"] == row["CURRENT_HIGH"]

    def can_sell(self, trade: Trade, row: pd.Series) -> bool:
        return row["LOW"] <= trade.stop_loss

    def can_update_sell_price(self, trade: Trade, row: pd.Series):
        return row["CURRENT_LOW"] > trade.stop_loss

    def execute(self) -> List[HighLowTrade]:
        self.preprocess()

        trades = []
        current_trade = None

        for _, row in self.df.iterrows():
            if current_trade is None and self.can_buy(row):
                current_trade = HighLowTrade(
                    buy_price=row["LTP"],
                    start_date=row["DATE"],
                    initial_stop_loss=row["CURRENT_LOW"],
                    stop_loss=row["CURRENT_LOW"],
                )
            else:

                if current_trade is not None and self.can_update_sell_price(
                    current_trade, row
                ):
                    current_trade.update_stop_loss(row["CURRENT_LOW"])

                if current_trade is not None and row["LOW"] <= current_trade.stop_loss:
                    current_trade.sell(row["DATE"])
                    trades.append(current_trade)
                    current_trade = None

        if current_trade is not None:
            current_trade.update_stop_loss(self.df.iloc[-1]["LTP"])
            current_trade.sell(self.df.iloc[-1]["DATE"])

            trades.append(current_trade)

        return trades
    
    def breakout(self, today: dict) -> bool:
        pass

    def get_stop_loss(self):
        pass
