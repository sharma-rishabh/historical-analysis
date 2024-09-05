import os
from pathlib import Path
import pandas as pd
from typing import Dict
from datetime import date, datetime, timedelta
from jugaad_data.nse import stock_df, NSELive
from invest_assist.models import OptionPortfolio, Portfolio
from invest_assist.strategies import FortyTwenty, MovingAverage
from invest_assist.strategies.ThirtyThirtyThree import ThirtyThirtyThree
from invest_assist.strategies.ThirtyTwentyNine import ThirtyTwentyNine


strategy_class: Dict[str, Dict] = {
    "FortyTwenty": {"class": FortyTwenty, "min_days_required": 100},
    "ThirtyTwentyNine": {"class": ThirtyTwentyNine, "min_days_required": 100},
    "ThirtyThirtyThree": {"class": ThirtyThirtyThree, "min_days_required": 100},
    "MovingAverage": {"class": MovingAverage, "min_days_required": 100},
}


def get_historical_data(symbol: str, days: int) -> pd.DataFrame:
    today = date.today()
    ten_years_ago = today - timedelta(days=days)
    df = stock_df(symbol=symbol, from_date=ten_years_ago, to_date=today, series="EQ")

    df = df.drop_duplicates()
    return df

def get_current_price(symbol:str) -> float:
    nse = NSELive()
    q = nse.stock_quote(symbol)
    return q["priceInfo"]["lastPrice"]

def get_stop_loss(symbol: str, strategy_name: str) -> float:
    strategy = strategy_class[strategy_name]["class"]
    days = strategy_class[strategy_name]["min_days_required"]

    stock_data = get_historical_data(symbol, days)
    return strategy(stock_data).get_stop_loss()

def get_breakout(symbol: str, strategy_name: str) -> bool:
    strategy = strategy_class[strategy_name]["class"]
    days = strategy_class[strategy_name]["min_days_required"]

    try:
        nse = NSELive()
        today = nse.stock_quote(symbol)['priceInfo']
        stock_data = get_historical_data(symbol, days)
    except:
         return False


    return strategy(stock_data).breakout(today)


def validate_path(ctx, param, value):
    if value is None:
        return None

    prefix = os.getenv("PORTFOLIO_HOME")
    return os.path.join(prefix, f"{value}.json")

def read_portfolio(path: Path) -> Portfolio:
        with open(path, "r") as raw_portfolio:
            return Portfolio.model_validate_json(raw_portfolio.read())

def write_portfolio(path: Path, portfolio: Portfolio):
    with open(path, "w") as file:
        file.write(portfolio.model_dump_json(indent=4))


def load_options_portfolio(options_path) -> OptionPortfolio:
    if options_path is None:
        raise Exception("OPTIONS_PATH not set")

    option_path = Path(f"{options_path}/OptionPortfolio.json")

    if not option_path.exists():
        option_portfolio = OptionPortfolio(
            date=datetime.today().date(), options=[], risk=0.2
        )
        option_portfolio.add_cash(15000)
        return option_portfolio

    with open(option_path, "r") as file:
        option_portfolio = OptionPortfolio.model_validate_json(file.read())
        return option_portfolio
    
def load_watch_list_portfolio(options_path: str | None, date: datetime) -> OptionPortfolio:
    if options_path is None:
        raise Exception("OPTIONS_PATH not set")

    option_path = Path(f"{options_path}/{date.date()}.json")
    if not option_path.exists():
        raise Exception(f"Options for {date.date()} not found. {type(date)}")

    with open(option_path, "r") as file:
        option_portfolio = OptionPortfolio.model_validate_json(file.read())

    return option_portfolio