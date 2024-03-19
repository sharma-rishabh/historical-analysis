import os
import click
from tabulate import tabulate

from invest_assist.models import Portfolio, Holding
from .utils import read_portfolio
from .describe import print_summary


@click.command()
def list_portfolios():

    """
    Show tables describing the value of the portfolios.
    """


    portfolio_dir = os.getenv("PORTFOLIO_HOME")
    files = os.listdir(portfolio_dir)

    for file in files:
        portfolio_path = os.path.join(portfolio_dir,file)
        portfolio = read_portfolio(portfolio_path)
        portfolio_name = file.split(".json")[0]
        click.echo("\n")
        click.secho(portfolio_name, bold=True)
        print_summary(portfolio)
        click.echo("\n")




