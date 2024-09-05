from datetime import date, datetime
import os
from pathlib import Path
import click
from tabulate import tabulate

from invest_assist.commands.utils import load_options_portfolio, load_watch_list_portfolio
from invest_assist.models import Option, OptionPortfolio
from jugaad_data.nse import NSELive

nseLive = NSELive()

def get_option(option:Option):
    return [
        option.symbol,
        option.option_type,
        option.strike,
        option.expiry,
        option.initial_price,
        option.change(),
        option.current_price,
        option.expected_hit,
        option.underlying_value,
        option.expected_change
    ]

def get_watch_list_headers(option_portfolio: OptionPortfolio):
    total_invested_header = click.style("Total Invested", bold=True)
    total_invested = click.style(str(option_portfolio.total_invested()), bold=True)

    change_header = click.style("Change", bold=True)
    change = click.style(str(option_portfolio.change()), bold=True)

    current_value_header = click.style("Current Value", bold=True)
    current_value = click.style(str(option_portfolio.current_value()), bold=True)

    data = [
        [
            total_invested_header,
            total_invested,
            "",
            change_header,
            change,
            "",
            current_value_header,
            current_value,
        ],
    ]
    return tabulate(data, tablefmt="grid", numalign="right")

def get_portfolio_headers(option_portfolio: OptionPortfolio):
    total_invested_header = click.style("Total Invested", bold=True)
    total_invested = click.style(str(option_portfolio.total_invested()), bold=True)

    change_header = click.style("Change", bold=True)
    change = click.style(str(option_portfolio.change()), bold=True)

    current_value_header = click.style("Current Value", bold=True)
    current_value = click.style(str(option_portfolio.current_value()), bold=True)

    cash_input_header = click.style("Cash Input", bold=True)
    cash_input = click.style(str(option_portfolio.cash_input), bold=True)

    overall_returns_header = click.style("Overall Returns", bold=True)
    overall_returns = click.style(str(option_portfolio.overall_returns()), bold=True)

    remaining_capital_header = click.style("Remaining Capital", bold=True)
    remaining_capital = click.style(str(option_portfolio.remaining_capital()), bold=True)

    data = [
        [
            total_invested_header,
            total_invested,
            "",
            change_header,
            change,
            "",
            current_value_header,
            current_value,
            "",
        ],
        [
            cash_input_header,
            cash_input,
            "",
            overall_returns_header,
            overall_returns,
            "",
            remaining_capital_header,
            remaining_capital,
        ],
    ]
    return tabulate(data, tablefmt="grid", numalign="right")

@click.command()
@click.option("--portfolio", "-p", is_flag=True, help="show portfolio not watch list")
@click.option(
    "--date",
    "-d",
    type=click.DateTime(formats=["%d-%m-%Y"]),
    default=date.today().strftime("%d-%m-%Y"),
    required=False,
    help="Describe which dates options",
)
def describe_option(date: datetime, portfolio: bool):
    """Describe options for a given date."""

    options_path = os.getenv("OPTIONS_PATH")
    if portfolio:
        option_portfolio = load_options_portfolio(options_path)
        option_path = Path(f"{options_path}/OptionPortfolio.json")
    else:
        option_portfolio = load_watch_list_portfolio(options_path, date)
        option_path = Path(f"{options_path}/{date.date()}.json")

    click.secho("UPDATING OPTIONS", bold=True)

    quotes_data = {}
    with click.progressbar(option_portfolio.options) as options:
        for option in options:
            if option.symbol not in quotes_data:
                try:
                    quote_data = nseLive.stock_quote_fno(option.symbol)
                    quotes_data[option.symbol] = quote_data
                except:
                    print("Couldn't fetch quote for ", option.symbol)

    option_portfolio.update(quotes_data)

    if portfolio:
        option_portfolio.sell_options()

    with open(option_path,"w") as file:
        file.write(option_portfolio.model_dump_json(indent=4))

    click.secho("OPTIONS UPDATED", bold=True)

    click.secho("DESCRIBING OPTIONS", bold=True)

    table = (
        get_portfolio_headers(option_portfolio)
        if portfolio
        else get_watch_list_headers(option_portfolio)
    )
    click.secho(table)

    headers = [
        "Symbol",
        "Type",
        "Strike",
        "Expiry",
        "Initial Price",
        "Change",
        "Current Price",
        "Expected Hit Date",
        "Underlying Price",
        "Expected Change",
    ]

    data = [get_option(option) for option in option_portfolio.active_options()]

    data_table = tabulate(data, headers, tablefmt="grid", numalign="right")
    click.echo(data_table)
