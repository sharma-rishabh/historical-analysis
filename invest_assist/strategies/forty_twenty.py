import pandas as pd
from trade import Trade
from typing import List
from .strategy import Strategy
from datetime import datetime


class FortyTwenty(Strategy):
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

                if current_trade is not None and self.can_update_sell_price(
                    current_trade, row
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

    def get_stop_loss(self) -> float:
        self.preprocess()
        return self.df.iloc[-1]["LOWEST_20D"]

    def add_todays_data(self, today: dict):
        new_row = self.df.iloc[-1].copy()
        new_row["index"] = new_row['index'] + 1
        new_row["DATE"] = datetime.now()
        new_row["LTP"] = today["lastPrice"]
        new_row["OPEN"] = today["open"]
        new_row["HIGH"]= today["intraDayHighLow"]["max"]
        new_row["LOW"]= today["intraDayHighLow"]["min"]
        new_row['40D_HIGH'] = new_row['HIGH'] if new_row['HIGH'] > new_row['40D_HIGH'] else new_row['40D_HIGH']
        new_row['LOWEST_20D'] = new_row['LOW'] if new_row['LOW'] < new_row['LOWEST_20D'] else new_row['LOWEST_20D']


        self.df.loc[len(self.df) + 1] = new_row

    def breakout(self, today: dict) -> bool:
        self.preprocess()

        if len(self.df) <= 0:
            return False
        
        self.add_todays_data(today)
        last_row = self.df.iloc[-1]
        return last_row['HIGH'] >= last_row['40D_HIGH']
