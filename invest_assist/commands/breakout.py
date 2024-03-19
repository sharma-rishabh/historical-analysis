import click
import pandas as pd
from .utils import get_breakout


@click.command()
@click.option(
    "--strategy-name",
    type=str,
    required=True,
    help="Strategy for which you want to see breakouts.",
)
@click.option(
    "--all",
    is_flag=True,
    help="Run breakout against all stocks"
)
@click.option(
    "-n",
    type=int,
    required=False,
    default=50,
    help="Top n companies you want to check for.",
)
def breakout(strategy_name: str,all:bool, n:int):
    """
    Get a list of all the companies that broke out today for a particular strategy.
    """
    
    df = pd.read_csv("company_list.csv")
    if all:
        n = len(df)
    symbols = df.head(n)["Symbol"].tolist()

    breakouts = [symbol for symbol in symbols if get_breakout(symbol, strategy_name)]

    click.echo(','.join(breakouts))
