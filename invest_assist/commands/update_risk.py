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
    "--new-risk",
    type=float,
    required=True,
    help="To update the capital for the portfolio.",
)
def update_risk(portfolio: click.types.Path, new_risk: float):
    """
    Update risk of a portfolio as you increase your capital.
    """

    parsed_pf = read_portfolio(portfolio)
    new_risk = parsed_pf.update_risk(new_risk)
    write_portfolio(portfolio, parsed_pf)
    bold_risk = click.style(f"{new_risk}", bold=True)

    click.echo(f"Risk update to ${bold_risk}")
