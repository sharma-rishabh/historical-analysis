import click
from .update import update
from .buy import buy
from .historical_analysis import historical_analysis
from .create_portfolio import create_portfolio
from .sell import sell
from .describe import describe


@click.group()
def stock():
    pass


stock.add_command(buy)
stock.add_command(historical_analysis)
stock.add_command(create_portfolio)
stock.add_command(update)
stock.add_command(sell)
stock.add_command(describe)
