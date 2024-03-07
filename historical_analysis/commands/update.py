import click

from models.portfolio import Holding
from .utils import validate_path, read_portfolio, get_stop_loss, write_portfolio, get_current_price


def print_updated_stop_loss(holding: Holding):
    new_stop_loss = click.style(str(holding.stop_loss), bold=True)
    symbol = click.style(holding.symbol, bold=True)
    click.echo(f"Updated stop loss of  {symbol} to {new_stop_loss}")


@click.command()
@click.option(
    "--portfolio",
    type=click.Path(),
    callback=validate_path,
    required=True,
    help="Portfolio for which you want to update the stop loss.",
)
def update(portfolio: click.Path):
    parsed_pf = read_portfolio(portfolio)
    updated_holdings = [holding for holding in parsed_pf.active_stocks() if holding.update_stop_loss(get_stop_loss(holding.symbol, holding.strategy))]

    for holding in parsed_pf.active_stocks():
        holding.update_current_price(get_current_price(holding.symbol))

    write_portfolio(portfolio, parsed_pf)

    for holding in updated_holdings:
        print_updated_stop_loss(holding)
    
    if len(updated_holdings) == 0:
        click.echo("No stop loss needs update.")
