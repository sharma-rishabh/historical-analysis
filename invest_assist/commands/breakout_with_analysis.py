import click
import pandas as pd
from io import StringIO
from datetime import date
from jugaad_data.nse import stock_df
from invest_assist.company_list import listings
from invest_assist.analyzer import Analyzer
from invest_assist.models import Portfolio
from .utils import get_breakout, get_current_price, get_stop_loss, read_portfolio, strategy_class, validate_path
from .historical_analysis import print_analysis_result
from .buy import print_buying_result

def get_buying_data(portfolio: Portfolio, symbol:str, strategy_name: str):
    current_price = get_current_price(symbol)
    strategy = strategy_class[strategy_name]["class"]
    historical_analysis_result = Analyzer(symbol, portfolio, strategy, 3650, stock_df).analyse()
    stop_loss = get_stop_loss(symbol, strategy_name)

    return portfolio.buy_stock(
        symbol,
        current_price,
        current_price,
        stop_loss,
        1.0,
        strategy_name,
        date.today(),
        historical_analysis_result,
        True
    )


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
    
    """
    Get a list of all the companies that broke out today for a particular strategy along with their historical-analysis.
    """

    df = pd.read_csv(StringIO(listings))

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

        results.sort(key=lambda x: x.returns)

        

    for result in results:
        print_analysis_result(result.symbol, strategy_name, result)
        holding = get_buying_data(
            parsed_pf,
            result.symbol,
            strategy_name
        )
        print_buying_result(holding, True)
