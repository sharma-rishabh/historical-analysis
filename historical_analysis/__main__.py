import math
import os
import click
from datetime import date, datetime, timedelta
import json
from models.portfolio import Portfolio, Holding, HistoricalAnalysisResult
from jugaad_data.nse import stock_df, NSELive
import pandas as pd
from cumulative_analysis_result import CumulativeAnalysisResult
from strategies.forty_twenty import FortyTwenty
from analyzer import Analyzer
from risk_profile import RiskProfile
from typing import Dict

strategy_class: Dict[str, Dict] = {
    "FortyTwenty": {"class":FortyTwenty, "min_days_required":100},
}


def print_analysis_result(
    symbol: str, strategy_name: str, cumulative_results: CumulativeAnalysisResult
):
    is_profitable = cumulative_results.average_return_on_risk > 0
    return_color = "green" if is_profitable else "red"
    are_enough_trades = len(cumulative_results.trade_analysis) > 20
    trade_color = "green" if are_enough_trades else "red"
    white = "bright_white"

    returns = click.style(
        f" {cumulative_results.average_return_on_risk} ", bg=return_color, fg=white
    )

    days = click.style(f"{cumulative_results.average_days}", bold=True)

    trades = click.style(
        f" {len(cumulative_results.trade_analysis)} ", bg=trade_color, fg=white
    )

    click.echo("\n\n")
    click.secho(f"{symbol} with {strategy_name}", bold=True)
    click.echo(f"Average return on risk: {returns}")
    click.echo(f"Average days taken: {days}")
    click.echo(f"Total Trades: {trades}")
    click.echo(
        f"Profitable Trades: {round(cumulative_results.profitable_trades * 100, 2)}%"
    )
    click.echo(f"Profitable trade returns: {cumulative_results.average_profit_return}")


def get_historical_data(symbol: str, days: int) -> pd.DataFrame:
    today = date.today()
    ten_years_ago = today - timedelta(days=days)
    df = stock_df(symbol=symbol, from_date=ten_years_ago, to_date=today, series="EQ")

    df = df.drop_duplicates()
    return df


@click.group()
def stock():
    pass


@stock.command()
@click.option("--symbols", type=str, required=True, help="Comma separated NSE symbols.")
@click.option(
    "--portfolio",
    type=click.types.File("r"),
    required=True,
    help="Portfolio against which you want to run the analysis",
)
@click.option(
    "--strategies",
    type=str,
    required=True,
    help="Comma separated strategies you want to execute on the symbols.",
)
@click.option(
    "--years",
    type=int,
    default=10,
    required=False,
    help="How much historical data should the analysis be ran on.",
)
def historical_analysis(
    symbols: str, portfolio: click.types.File, strategies: str, years: int
):
    """
    Run historical analysis based on the given portfolio against multiple symbols and strategies.
    """
    symbols = symbols.split(",")
    stock_data = [get_historical_data(symbol, years*365) for symbol in symbols]
    parsed_pf = Portfolio.model_validate_json(portfolio.read())
    profile = RiskProfile(parsed_pf.capital, parsed_pf.risk_percent)
    parsed_strategies = [strategy_class[name]["class"] for name in strategies.split(",")]

    for symbol, data in zip(symbols, stock_data):
        trades_per_strategy = [
            strategy(data).execute() for strategy in parsed_strategies
        ]

        results = [
            Analyzer(trades, profile).analyse() for trades in trades_per_strategy
        ]

        [
            print_analysis_result(symbol, strategy_name, result)
            for result, strategy_name in zip(results, strategies.split(","))
        ]


def print_buying_result(holding: Holding):
    has_bought = holding.units > 0
    bg_color = 'green' if has_bought else 'red'
    text = f"Bought {holding.units} units of {holding.symbol} for Rs {round(holding.units * holding.buying_price, 2)}" if has_bought else f"Couldn't buy {holding.symbol}"
    click.secho(text, bg=bg_color, fg='bright_white')


def validate_path(ctx, param, value):
    if value is None:
        return None

    prefix = "/Users/rishabh/workspace/python/projects/historical_analysis"
    return os.path.join(prefix, f"{value}.json")


@stock.command()
@click.option(
    "--symbol",
    type=str,
    required=True,
    help="Symbol of the stock you want to invest in",
)
@click.option(
    "--buying-price",
    type=float,
    required=True,
    help="What is the buying price for this stock."
)
@click.option(
    "--portfolio",
    type=click.Path(),
    callback=validate_path,
    required=True,
    help="Portfolio for which you want to buy this stock.",
)
@click.option(
    "--strategy-name",
    type=str,
    required=True,
    help="Strategy you want to execute for the stock.",
)
@click.option(
    "--buy-date",
    type=click.DateTime(formats=["%d-%m-%Y"]),
    default=date.today().strftime("%d-%m-%Y"),
    required=False,
    help="The buy date in the format DD-MM-YYYY",
)
@click.option(
    "--buying-capacity",
    type=float,
    required=False,
    default=1.0,
    help="How much of the remaining capital you wish to invest in the stock.",
)
def buy(
        symbol:str,
        buying_price: float,
        portfolio: click.types.Path,
        strategy_name:str,
        buy_date:datetime,
        buying_capacity:float
    ):

    """
    Buy a stock by giving a symbol, portfolio and strategy and the results are stored back in the portfolio. The historical analysis result is stored for the last 10 years.
    """

    nse = NSELive()
    q = nse.stock_quote(symbol)
    current_price: float = q['priceInfo']['lastPrice']

    strategy = strategy_class[strategy_name]['class']
    days = strategy_class[strategy_name]["min_days_required"]

    stock_data = get_historical_data(symbol, days)
    stop_loss = strategy(stock_data).get_stop_loss()

    with open(portfolio, 'r') as raw_portfolio:
        parsed_pf = Portfolio.model_validate_json(raw_portfolio.read())


    ten_year_stock_data = get_historical_data(symbol, 3650)
    trades = strategy(ten_year_stock_data).execute()
    profile = RiskProfile(parsed_pf.capital, parsed_pf.risk_percent)
    result = Analyzer(trades, profile).analyse()

    historical_analysis_result = HistoricalAnalysisResult(
        returns=result.average_return_on_risk,
        days_per_return=result.average_days,
        total_trades=len(trades),
        winning_percentage=result.profitable_trades
    )

    holding = parsed_pf.buy_stock(symbol, current_price, buying_price, stop_loss,buying_capacity,strategy_name,buy_date,historical_analysis_result)

    with open(portfolio, "w") as file:
        file.write(parsed_pf.model_dump_json())

    print_buying_result(holding)


@stock.command()
@click.option(
    "--portfolio-name",
    type=click.Path(),
    callback=validate_path,
    required=True,
    help="Name of the portfolio you want to create.",
)
@click.option(
    "--capital",
    type=float,
    required=True,
    help="Capital you want to use in the portfolio"
)
@click.option(
    "--risk-percent",
    type=float,
    required=True,
    help="How much risk you are going to take per stock in your portfolio [0-1]"
)
def create_portfolio(portfolio_name: click.types.Path, capital: float, risk_percent: float):
    portfolio = Portfolio(capital=capital, risk_percent=risk_percent, holdings=[])

    with open(portfolio_name, "w") as file:
        file.write(portfolio.model_dump_json())
    
    click.secho(f"Portfolio was created.", bold=True)
    



stock()
