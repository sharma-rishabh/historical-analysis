import click
from .utils import (
    validate_path,
    get_current_price,
    get_stop_loss,
    read_portfolio,
    write_portfolio,
    strategy_class,
)
from jugaad_data.nse import stock_df
from datetime import datetime, date
from invest_assist.models import Holding
from invest_assist.analyzer import Analyzer


def print_buying_result(holding: Holding, info_only: bool):
    has_bought = holding.units > 0
    bg_color = "green" if has_bought else "red"
    append = "You could buy" if info_only else "Bought"
    append_couldnt = "Cannot buy" if info_only else "Couldn't buy" 
    text = (
        f"{append} {holding.units} units of {holding.symbol} for Rs {round(holding.units * holding.buying_price, 2)}, Stop-loss {holding.stop_loss}"
        if has_bought
        else f"{append_couldnt} {holding.symbol}, Price: {holding.buying_price}, Risk per unit: {round(holding.buying_price - holding.stop_loss)}"
    )
    click.secho(text, bg=bg_color, fg="bright_white")


@click.command()
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
    help="What is the buying price for this stock.",
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
@click.option("--info-only", is_flag=True, help="Simulate the buy only don't actually store the results.")
def buy(
    symbol: str,
    buying_price: float,
    portfolio: click.types.Path,
    strategy_name: str,
    buy_date: datetime,
    buying_capacity: float,
    info_only: bool
):
    """
    Buy a stock by giving a symbol, portfolio and strategy and the results are stored back in the portfolio. The historical analysis result is stored for the last 10 years.
    """

    strategy = strategy_class[strategy_name]["class"]
    current_price = get_current_price(symbol)
    stop_loss = get_stop_loss(symbol, strategy_name)
    parsed_pf = read_portfolio(portfolio)

    historical_analysis_result = Analyzer(symbol, parsed_pf, strategy, 3650, stock_df).analyse()

    holding = parsed_pf.buy_stock(
        symbol,
        current_price,
        buying_price,
        stop_loss,
        buying_capacity,
        strategy_name,
        buy_date,
        historical_analysis_result,
        info_only
    )

    if not info_only:
        write_portfolio(portfolio, parsed_pf)

    print_buying_result(holding, info_only)
