import click
from . import  validate_path, strategy_class, get_historical_data
from datetime import datetime, date
from jugaad_data.nse import NSELive
from models import Holding, HistoricalAnalysisResult, Portfolio
from analyzer import Analyzer
from risk_profile import RiskProfile

def print_buying_result(holding: Holding):
    has_bought = holding.units > 0
    bg_color = "green" if has_bought else "red"
    text = (
        f"Bought {holding.units} units of {holding.symbol} for Rs {round(holding.units * holding.buying_price, 2)}"
        if has_bought
        else f"Couldn't buy {holding.symbol}"
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
def buy(
    symbol: str,
    buying_price: float,
    portfolio: click.types.Path,
    strategy_name: str,
    buy_date: datetime,
    buying_capacity: float,
):
    """
    Buy a stock by giving a symbol, portfolio and strategy and the results are stored back in the portfolio. The historical analysis result is stored for the last 10 years.
    """

    nse = NSELive()
    q = nse.stock_quote(symbol)
    current_price: float = q["priceInfo"]["lastPrice"]

    strategy = strategy_class[strategy_name]["class"]
    days = strategy_class[strategy_name]["min_days_required"]

    stock_data = get_historical_data(symbol, days)
    stop_loss = strategy(stock_data).get_stop_loss()

    with open(portfolio, "r") as raw_portfolio:
        parsed_pf = Portfolio.model_validate_json(raw_portfolio.read())

    ten_year_stock_data = get_historical_data(symbol, 3650)
    trades = strategy(ten_year_stock_data).execute()
    profile = RiskProfile(parsed_pf.capital, parsed_pf.risk_percent)
    result = Analyzer(trades, profile).analyse()

    historical_analysis_result = HistoricalAnalysisResult(
        returns=result.average_return_on_risk,
        days_per_return=result.average_days,
        total_trades=len(trades),
        winning_percentage=result.profitable_trades,
    )

    holding = parsed_pf.buy_stock(
        symbol,
        current_price,
        buying_price,
        stop_loss,
        buying_capacity,
        strategy_name,
        buy_date,
        historical_analysis_result,
    )

    with open(portfolio, "w") as file:
        file.write(parsed_pf.model_dump_json())

    print_buying_result(holding)
