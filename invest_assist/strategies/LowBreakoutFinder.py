import pandas as pd
from invest_assist.trade import Trade
from typing import List
from .strategy import Strategy
from datetime import datetime


class LowBreakoutFinder:
    def __init__(self, df: pd.DataFrame, breakout_days: int):
        self.df = df.copy()
        self.breakout_days = breakout_days

    def preprocess(self):
        self.df = self.df[::-1].reset_index(drop=True)
        self.df = self.df.drop_duplicates()

        self.df["BREAKOUT"] = self.df["LOW"].rolling(window=self.breakout_days).min()

        self.df.dropna(how="any", inplace=True)
        self.df = self.df.reset_index()

    def breakout(self) -> bool:
        self.preprocess()
        row = self.df.iloc[-1]
        return row["LOW"] <= row["BREAKOUT"]
