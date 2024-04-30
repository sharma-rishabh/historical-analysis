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
