import click

from .utils import strategy_class, validate_path, read_portfolio
from models.portfolio import Portfolio, HistoricalAnalysisResult
from analyzer import Analyzer


def print_analysis_result(
    symbol: str, strategy_name: str, historical_results: HistoricalAnalysisResult
):
    is_profitable = historical_results.returns > 0
    return_color = "green" if is_profitable else "red"
    are_enough_trades = historical_results.total_trades > 20
    trade_color = "green" if are_enough_trades else "red"
    white = "bright_white"

    returns = click.style(
        f" {historical_results.returns} ", bg=return_color, fg=white
    )

    days = click.style(f"{historical_results.days_per_return}", bold=True)

    trades = click.style(
        f" {historical_results.total_trades} ", bg=trade_color, fg=white
    )

    click.echo("\n\n")
    click.secho(f"{symbol} with {strategy_name}", bold=True)
    click.echo(f"Average return on risk: {returns}")
    click.echo(f"Average days taken: {days}")
    click.echo(f"Total Trades: {trades}")
    click.echo(
        f"Profitable Trades: {round(historical_results.winning_percentage * 100, 2)}%"
    )


@click.command()
@click.option("--symbols", type=str, required=True, help="Comma separated NSE symbols.")
@click.option(
    "--portfolio",
    type=click.Path(),
    callback=validate_path,
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

    parsed_pf = read_portfolio(portfolio)
    
    parsed_strategies = [
        strategy_class[name]["class"] for name in strategies.split(",")
    ]

    for symbol in symbols:
        
        results = [
            Analyzer(symbol, parsed_pf, strategy, 365*years).analyse()
              for strategy in parsed_strategies
        ]

        [
            print_analysis_result(symbol, strategy_name, result)
            for result, strategy_name in zip(results, strategies.split(","))
        ]
