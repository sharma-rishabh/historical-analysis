import pandas as pd
from invest_assist.models.OptionTrade import OptionTrade
from invest_assist.trade import Trade
from typing import List
from datetime import datetime


class PutLowBreakoutFinder:

    def __init__(self, df: pd.DataFrame, breakout_days: int, days_to_expiry: int):
        self.df = df.copy()
        self.breakout_days = breakout_days
        self.days_to_expiry = days_to_expiry

    def preprocess(self):
        if "BREAKOUT" in self.df.columns:
            return self.df
        self.df = self.df[::-1].reset_index(drop=True)
        self.df = self.df.drop_duplicates()

        self.df["BREAKOUT"] = self.df["LOW"].rolling(window=self.breakout_days).min()

        self.df.dropna(how="any", inplace=True)
        self.df = self.df.reset_index()

    def should_start_analysis(self, row: pd.Series) -> bool:
        return row["LOW"] == row["BREAKOUT"]

    def is_trough_lower(self, row: pd.Series, trade: OptionTrade) -> bool:
        return row["LOW"] <= trade.current_limit

    def should_stop_analysis(self, row: pd.Series, trade: OptionTrade) -> bool:
        return (row["DATE"] - trade.start_date).days >= self.days_to_expiry

    def find_change_till_expiry(self) -> List[OptionTrade]:
        self.preprocess()
        trades = []
        current_trade = None

        for _, row in self.df.iterrows():
            if current_trade is None and self.should_start_analysis(row):
                current_trade = OptionTrade(
                    breakout=self.breakout_days,
                    start_price=row["LTP"],
                    change=0,
                    days=0,
                    current_limit=row["LOW"],
                    start_date=row["DATE"],
                )

            if current_trade is not None and self.should_stop_analysis(
                row, current_trade
            ):
                current_trade.update_change(row["LOW"], row["DATE"])
                trades.append(current_trade)
                current_trade = None

        if current_trade is not None:
            trades.append(current_trade)
            current_trade = None

        return trades

    def find_troughs(self) -> List[Trade]:
        self.preprocess()

        trades = []
        current_trade = None

        for _, row in self.df.iterrows():
            if current_trade is None and self.should_start_analysis(row):
                current_trade = OptionTrade(
                    breakout=self.breakout_days,
                    start_price=row["LTP"],
                    change=0,
                    days=0,
                    current_limit=row["LOW"],
                    start_date=row["DATE"],
                )

            if current_trade is not None and self.is_trough_lower(row, current_trade):
                current_trade.update_change(row["LOW"], row["DATE"])

            if current_trade is not None and self.should_stop_analysis(
                row, current_trade
            ):
                trades.append(current_trade)
                current_trade = None

        if current_trade is not None:
            trades.append(current_trade)
            current_trade = None

        return trades

    def get_stop_loss(self) -> float:
        self.preprocess()
        return self.df.iloc[-1]["LOWEST_20D"]

    def add_todays_data(self, today: dict):
        new_row = self.df.iloc[-1].copy()
        new_row["index"] = new_row["index"] + 1
        new_row["DATE"] = datetime.now()
        new_row["LTP"] = today["lastPrice"]
        new_row["OPEN"] = today["open"]
        new_row["HIGH"] = today["intraDayHighLow"]["max"]
        new_row["LOW"] = today["intraDayHighLow"]["min"]
        new_row["40D_HIGH"] = (
            new_row["HIGH"]
            if new_row["HIGH"] > new_row["40D_HIGH"]
            else new_row["40D_HIGH"]
        )
        new_row["LOWEST_20D"] = (
            new_row["LOW"]
            if new_row["LOW"] < new_row["LOWEST_20D"]
            else new_row["LOWEST_20D"]
        )

        self.df.loc[len(self.df) + 1] = new_row

    def breakout(self, today: dict) -> bool:
        self.preprocess()

        if len(self.df) <= 0:
            return False

        self.add_todays_data(today)
        last_row = self.df.iloc[-1]
        return last_row["HIGH"] >= last_row["40D_HIGH"]
