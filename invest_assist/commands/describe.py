import click
from tabulate import tabulate

from invest_assist.models import Portfolio, Holding
from .utils import validate_path, read_portfolio


def get_current_value(current_value: float, invested: float) -> str:
    is_in_profit = current_value > invested
    color = "bright_green" if is_in_profit else "bright_red"
    return click.style(f"{current_value}", fg=color, bold=True)


def get_returns(returns: float) -> str:
    is_in_profit = returns > 0
    color = "bright_green" if is_in_profit else "bright_red"
    return click.style(f"{round(returns * 100, 2)}", fg=color, bold=True)


def print_summary(portfolio: Portfolio):
    current_value_header = click.style("Current Value", bold=True)
    current_value = get_current_value(portfolio.current_value(), portfolio.invested())

    returns_header = click.style("Returns", bold=True)
    returns = get_returns(portfolio.return_percent())

    invested_header = click.style("Invested", bold=True)
    invested = click.style(f"{portfolio.invested()}", bold=True)

    remaining_capital_header = click.style("Remaining Capital", bold=True)
    remaining_capital = click.style(f"{portfolio.remaining_capital()}", bold=True)

    cash_input_header = click.style("Cash Input", bold=True)
    cash_input = click.style(f"{portfolio.cash_input}", bold=True)

    overall_returns_header = click.style("Overall Returns", bold=True)
    overall_returns = get_returns(portfolio.overall_returns())

    data = [
        [
            current_value_header,
            current_value,
            "",
            returns_header,
            returns,
            "",
            overall_returns_header,
            overall_returns,
        ],
        [
            invested_header,
            invested,
            "",
            remaining_capital_header,
            remaining_capital,
            "",
            cash_input_header,
            cash_input,
        ],
    ]

    table = tabulate(data, tablefmt="grid", numalign="right")
    click.echo(table)


def get_holding(holding: Holding):
    is_more_than_buying_price = holding.current_price > holding.buying_price
    current_price_color = "bright_green" if is_more_than_buying_price else "bright_red"
    current_price = click.style(
        str(holding.current_price), bold=True, fg=current_price_color
    )

    is_profitable = holding.returns_on_risk() > 0
    return_color = "bright_green" if is_profitable else "bright_red"
    return_on_risk = click.style(
        str(round(holding.returns_on_risk(), 2)), bold=True, fg=return_color
    )

    is_profitable_currently = holding.stop_loss > holding.buying_price

    stop_loss_color = "bright_green" if is_profitable_currently else "bright_red"
    stop_loss = click.style(str(holding.stop_loss), bold=True, fg=stop_loss_color)

    return [
        holding.id,
        click.style(holding.symbol, bold=True),
        click.style(holding.strategy, bold=True),
        holding.units,
        current_price,
        holding.risk,
        return_on_risk,
        stop_loss,
        holding.buying_price,
    ]


@click.command()
@click.option(
    "--portfolio",
    type=click.Path(),
    callback=validate_path,
    required=True,
    help="Portfolio for which you want to buy this stock.",
)
def describe(portfolio: click.types.Path):
    """
    Show a table describing the value and holdings of a portfolio.
    """

    parsed_pf = read_portfolio(portfolio)
    click.clear()

    click.secho("\n\nSUMMARY", bold=True)
    print_summary(parsed_pf)

    click.secho("\n\nHOLDINGS", bold=True)
    holding_headers = [
        "Id",
        "Symbol",
        "Strategy",
        "Units",
        "LTP",
        "Risk",
        "RoR",
        "Stop Loss",
        "Buy Price",
    ]

    data = [get_holding(holding) for holding in parsed_pf.active_stocks()]
    table = tabulate(data, holding_headers, tablefmt="grid", numalign="right")
    click.echo(table)
