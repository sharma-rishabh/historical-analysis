import pandas as pd
from trade import Trade
from typing import List


class FortyTwenty:
    def __init__(self, df: pd.DataFrame):
        self.df = df.copy()

    def preprocess(self):
        self.df = self.df[::-1].reset_index(drop=True)
        self.df = self.df.drop_duplicates()

        self.df["40D_HIGH"] = self.df["HIGH"].rolling(window=40).max()
        self.df["LOWEST_20D"] = self.df["CLOSE"].rolling(window=20).min()
        self.df.dropna(how="any", inplace=True)
        self.df = self.df.reset_index()

    def can_buy(self, row: pd.Series) -> bool:
        return row["HIGH"] == row["40D_HIGH"]

    def can_sell(self, trade: Trade, row: pd.Series) -> bool:
        return row["LOW"] <= trade.stop_loss

    def can_update_sell_price(self, trade: Trade, row: pd.Series):
        return row["LOWEST_20D"] > trade.stop_loss

    def execute(self) -> List[Trade]:
        self.preprocess()

        trades = []
        current_trade = None

        for _, row in self.df.iterrows():

            if current_trade is None and self.can_buy(row):

                current_trade = Trade(
                        buy_price=row["LTP"],
                        start_date=row["DATE"],
                        initial_stop_loss=row["LOWEST_20D"],
                    )
            else:

                if (
                    current_trade is not None
                    and self.can_update_sell_price(current_trade, row)
                ):
                    current_trade.update_stop_loss(row["LOWEST_20D"])

                if current_trade is not None and row["LOW"] <= current_trade.stop_loss:
                    current_trade.sell(row["DATE"])
                    trades.append(current_trade)
                    current_trade = None

        if current_trade is not None:
            current_trade.stop_loss = self.df.iloc[-1]["LTP"]
            current_trade.sell(self.df.iloc[-1]["DATE"])

            trades.append(current_trade)

        return trades
