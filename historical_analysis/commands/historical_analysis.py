import click

from cumulative_analysis_result import CumulativeAnalysisResult
from . import strategy_class, get_historical_data
from models.portfolio import Portfolio
import pandas as pd
from analyzer import Analyzer
from risk_profile import RiskProfile


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


@click.command()
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
    stock_data = [get_historical_data(symbol, years * 365) for symbol in symbols]
    parsed_pf = Portfolio.model_validate_json(portfolio.read())
    profile = RiskProfile(parsed_pf.capital, parsed_pf.risk_percent)
    parsed_strategies = [
        strategy_class[name]["class"] for name in strategies.split(",")
    ]

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
