import click
from .utils import read_portfolio, validate_path, write_portfolio

@click.command()
@click.option(
    "--symbol",
    required=False,
    type=str,
    help="Symbol of stock you want to sell. It sells all the holdings with that symbol.",
)
@click.option("--id", required=False, type=int, help="Id of the stock you want to sell")
@click.option(
    "--selling-price",
    required=False,
    type=float,
    help="Send a selling price if you want to sell the stock at a price other than current stop loss",
)
@click.option(
    "--portfolio",
    type=click.Path(),
    callback=validate_path,
    required=True,
    help="Portfolio for which you want to buy this stock.",
)
def sell(
    symbol: str | None,
    id: int | None,
    selling_price: float | None,
    portfolio: click.types.Path,
):
    """
    Sell a stock by either using the symbol or id.
    """

    if not (symbol or id):
        raise click.UsageError(
            "Either symbol or id of the stock you want to sell is needed"
        )

    if symbol and id:
        raise click.UsageError("Please provide either id or symbol not both.")

    parsed_pf = read_portfolio(portfolio)
    selling_price = parsed_pf.sell_holdings(id, symbol, selling_price)
    

    symbol_or_id = symbol if symbol else id
    bold_symbol_or_id =  click.style(f"{symbol_or_id}", bold=True)
    bold_selling_price = click.style(f"{selling_price}", bold=True)

    write_portfolio(portfolio, parsed_pf)
    click.echo(f"Sold holding {bold_symbol_or_id} for {bold_selling_price}")
