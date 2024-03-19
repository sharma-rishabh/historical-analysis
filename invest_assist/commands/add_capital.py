import click
from .utils import read_portfolio, write_portfolio, validate_path


@click.command()
@click.option(
    "--portfolio",
    type=click.Path(),
    callback=validate_path,
    required=True,
    help="Portfolio for which you want to add capital.",
)
@click.option(
    "--amount",
    type=float,
    required=True,
    help="To update the capital for the portfolio.",
)
def add_capital(portfolio: click.types.Path, amount: float):
    parsed_pf = read_portfolio(portfolio)
    new_capital = parsed_pf.update_capital(amount)
    write_portfolio(portfolio, parsed_pf)
    bold_capital = click.style(f"{new_capital}", bold=True)
    
    click.echo(f"Capital update to ${bold_capital}")
