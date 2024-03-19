import time
import click
import pandas as pd

from invest_assist.analyzer import Analyzer
from .utils import get_breakout, read_portfolio, strategy_class, validate_path
from .historical_analysis import print_analysis_result

@click.command()
@click.option(
    "--strategy-name",
    type=str,
    required=True,
    help="Strategy for which you want to see breakouts.",
)
@click.option("--all", is_flag=True, help="Run breakout against all stocks")
@click.option(
    "-n",
    type=int,
    required=False,
    default=50,
    help="Top n companies you want to check for.",
)
@click.option(
    "--portfolio",
    type=click.Path(),
    callback=validate_path,
    required=True,
    help="Portfolio against which you want to run the analysis",
)
@click.option(
    "--years",
    type=int,
    default=10,
    required=False,
    help="How much historical data should the analysis be ran on.",
)
def breakout_with_analysis(
    strategy_name: str, all: bool, n: int, portfolio: click.types.File, years: int
):
    df = pd.read_csv("company_list.csv")
    if all:
        n = len(df)
    symbols = df.head(n)["Symbol"].tolist()

    click.secho("Filtering breakouts: ", bold=True)
    with click.progressbar(symbols) as syms:  
        breakouts = [symbol for symbol in syms if get_breakout(symbol, strategy_name)]

    strategy = strategy_class[strategy_name]["class"]
    parsed_pf = read_portfolio(portfolio)

    click.secho("\n\nRunning Analysis: ", bold=True)
    with click.progressbar(breakouts) as breaks: 
        results = [Analyzer(symbol, parsed_pf, strategy, 365 * years).analyse()
                   for symbol in breaks]

        results.sort(key=lambda x: x.returns, reverse=True)
    
    for result,symbol in zip(results,breakouts):
        print_analysis_result(symbol, strategy_name, result)
