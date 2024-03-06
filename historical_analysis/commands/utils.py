import os
import click
import pandas as pd
from typing import Dict
from datetime import date, timedelta
from jugaad_data.nse import stock_df
from strategies.forty_twenty import FortyTwenty



strategy_class: Dict[str, Dict] = {
    "FortyTwenty": {"class": FortyTwenty, "min_days_required": 100},
}


def get_historical_data(symbol: str, days: int) -> pd.DataFrame:
    today = date.today()
    ten_years_ago = today - timedelta(days=days)
    df = stock_df(symbol=symbol, from_date=ten_years_ago, to_date=today, series="EQ")

    df = df.drop_duplicates()
    return df


def validate_path(ctx, param, value):
    if value is None:
        return None

    prefix = "/Users/rishabh/workspace/python/projects/historical_analysis"
    return os.path.join(prefix, f"{value}.json")
