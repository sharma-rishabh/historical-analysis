import click
from .utils import  validate_path, write_portfolio
from models import Portfolio

@click.command()
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
    help="Capital you want to use in the portfolio",
)
@click.option(
    "--risk-percent",
    type=float,
    required=True,
    help="How much risk you are going to take per stock in your portfolio [0-1]",
)
def create_portfolio(
    portfolio_name: click.types.Path, capital: float, risk_percent: float
):
    """
    Create a new portfolio.
    """
    portfolio = Portfolio(capital=capital, risk_percent=risk_percent, holdings=[])

    write_portfolio(portfolio_name, portfolio)
    click.secho(f"Portfolio was created.", bold=True)
