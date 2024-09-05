import click
from .update import update
from .buy import buy
from .historical_analysis import historical_analysis
from .create_portfolio import create_portfolio
from .sell import sell
from .describe import describe
from .add_capital import add_capital
from .breakout import breakout
from .breakout_with_analysis import breakout_with_analysis
from .list_portfolios import list_portfolios
from .update_risk import update_risk
from .find_high_low import find_high_low
from .option_analysis import option_analysis
from .describe_options import describe_option


@click.group()
def stock():
    pass


stock.add_command(buy)
stock.add_command(historical_analysis)
stock.add_command(create_portfolio)
stock.add_command(update)
stock.add_command(sell)
stock.add_command(describe)
stock.add_command(add_capital)
stock.add_command(breakout)
stock.add_command(breakout_with_analysis)
stock.add_command(list_portfolios)
stock.add_command(update_risk)
stock.add_command(find_high_low)
stock.add_command(option_analysis)
stock.add_command(describe_option)
