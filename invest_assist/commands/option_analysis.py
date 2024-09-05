from datetime import datetime, timedelta
import json
import os
from pathlib import Path
from typing import Callable, Dict, List
import click
from invest_assist.OptionTradesAnalyzer import OptionTradeAnalyzer
from invest_assist.models import Option, OptionPortfolio, OptionTradeAnalysisResult
from invest_assist.strategies import (
    CallHighBreakoutFinder,
    CallLowBreakoutFinder,
    HighBreakoutFinder,
    LowBreakoutFinder,
    PutHighBreakoutFinder,
    PutLowBreakoutFinder,
)
from .utils import get_historical_data, load_options_portfolio
from jugaad_data.nse import NSELive

nseLive = NSELive()


@click.command()
@click.option("--all", is_flag=True, help="Run breakout against all stocks")
@click.option(
    "-n",
    type=int,
    required=False,
    default=50,
    help="Top n companies you want to check for.",
)
@click.option(
    "-r",
    type=int,
    required=False,
    default=3000,
    help="Top n companies you want to check for.",
)
@click.option(
    "--buy",
    is_flag=True,
    required=False,
    default=False,
    help="Buy the options",
)
@click.option(
    "--expiry-in",
    "-e",
    type=int,
    required=False,
    default=20,
    help="Expiry in days",
)
def option_analysis(n: int, all: bool, r: int, buy: bool, expiry_in: int):
    """Find high and low of n companies."""

    symbols = """AARTIIND
ABB
ABBOTINDIA
ABCAPITAL
ABFRL
ACC
ADANIENT
ADANIPORTS
ALKEM
AMBUJACEM
APOLLOHOSP
APOLLOTYRE
ASHOKLEY
ASIANPAINT
ASTRAL
ATUL
AUBANK
AUROPHARMA
AXISBANK
BAJAJ-AUTO
BAJAJFINSV
BAJFINANCE
BALKRISIND
BALRAMCHIN
BANDHANBNK
BANKBARODA
BATAINDIA
BEL
BERGEPAINT
BHARATFORG
BHARTIARTL
BHEL
BIOCON
BOSCHLTD
BPCL
BRITANNIA
BSOFT
CANBK
CANFINHOME
CHAMBLFERT
CHOLAFIN
CIPLA
COALINDIA
COFORGE
COLPAL
CONCOR
COROMANDEL
CROMPTON
CUB
CUMMINSIND
DABUR
DALBHARAT
DEEPAKNTR
DIVISLAB
DIXON
DLF
DRREDDY
EICHERMOT
ESCORTS
EXIDEIND
FEDERALBNK
GAIL
GLENMARK
GMRINFRA
GNFC
GODREJCP
GODREJPROP
GRANULES
GRASIM
GUJGASLTD
HAL
HAVELLS
HCLTECH
HDFCAMC
HDFCBANK
HDFCLIFE
HEROMOTOCO
HINDALCO
HINDCOPPER
HINDPETRO
HINDUNILVR
ICICIBANK
ICICIGI
ICICIPRULI
IDEA
IDFC
IDFCFIRSTB
IEX
IGL
INDHOTEL
INDIAMART
INDIGO
INDUSINDBK
INDUSTOWER
INFY
IOC
IPCALAB
IRCTC
ITC
JINDALSTEL
JKCEMENT
JSWSTEEL
JUBLFOOD
KOTAKBANK
LALPATHLAB
LAURUSLABS
LICHSGFIN
LT
LTF
LTIM
LTTS
LUPIN
M&M
M&MFIN
MANAPPURAM
MARICO
MARUTI
MCX
METROPOLIS
MFSL
MGL
MOTHERSON
MPHASIS
MRF
MUTHOOTFIN
NATIONALUM
NAUKRI
NAVINFLUOR
NESTLEIND
NMDC
NTPC
OBEROIRLTY
OFSS
ONGC
PAGEIND
PEL
PERSISTENT
PETRONET
PFC
PIDILITIND
PIIND
PNB
POLYCAB
POWERGRID
PVRINOX
RAMCOCEM
RBLBANK
RECLTD
RELIANCE
SAIL
SBICARD
SBILIFE
SBIN
SHREECEM
SHRIRAMFIN
SIEMENS
SRF
SUNPHARMA
SUNTV
SYNGENE
TATACHEM
TATACOMM
TATACONSUM
TATAMOTORS
TATAPOWER
TATASTEEL
TCS
TECHM
TITAN
TORNTPHARM
TRENT
TVSMOTOR
UBL
ULTRACEMCO
UNITDSPR
UPL
VEDL
VOLTAS
WIPRO
ZYDUSLIFE""".split(
        "\n"
    )

    if all:
        n = len(symbols)

    symbols = symbols[:n]

    historical_data = {}

    with click.progressbar(symbols) as syms:
        for i, symbol in enumerate(syms):
            try:
                stock_data = get_historical_data(symbol, 4000)
                historical_data[symbol] = stock_data
            except:
                print("couldn't fetch data for ", symbol, " at Index ", i)
                print("couldn't fetch data for symbol after", symbols[i-1])
                return False

    def find_high_breakout(stock_data):
        for i in range(100, 1, -1):
            if HighBreakoutFinder(stock_data, i).breakout():
                return i
        return 0

    def find_low_breakout(stock_data):
        for i in range(100, 1, -1):
            if LowBreakoutFinder(stock_data, i).breakout():
                return i
        return 0

    high_breakouts = {}
    low_breakouts = {}
    for symbol in historical_data.keys():
        stock_data = historical_data[symbol]
        high_breakouts[symbol] = find_high_breakout(stock_data)
        low_breakouts[symbol] = find_low_breakout(stock_data)

    call_low_analysis = {}
    call_high_analysis = {}
    put_high_analysis = {}
    put_low_analysis = {}

    for symbol in historical_data.keys():
        stock_data = historical_data[symbol]
        low_breakout = low_breakouts[symbol]
        high_breakout = high_breakouts[symbol]
        if low_breakout != 0:
            low_trades = CallLowBreakoutFinder(
                stock_data, low_breakouts[symbol], expiry_in
            ).find_peak()
            low_analysis = OptionTradeAnalyzer(low_trades).analyse()
            call_low_analysis[symbol] = low_analysis

            put_low_trades = PutLowBreakoutFinder(
                stock_data, low_breakouts[symbol], expiry_in
            ).find_troughs()
            low_analysis_put = OptionTradeAnalyzer(put_low_trades).analyse()
            put_low_analysis[symbol] = low_analysis_put

        if high_breakout != 0:
            high_trades = CallHighBreakoutFinder(
                stock_data, high_breakouts[symbol], expiry_in
            ).find_peak()
            high_analysis = OptionTradeAnalyzer(high_trades).analyse()
            call_high_analysis[symbol] = high_analysis

            put_high_trades = PutHighBreakoutFinder(
                stock_data, high_breakouts[symbol], expiry_in
            ).find_troughs()
            high_analysis_put = OptionTradeAnalyzer(put_high_trades).analyse()
            put_high_analysis[symbol] = high_analysis_put

    options_symbols = set(list(call_high_analysis.keys()) + list(call_low_analysis.keys()) + list(put_high_analysis.keys()) + list(put_low_analysis.keys()))
    options_data = {}
    quotes_data = {}

    with click.progressbar(options_symbols) as syms:
        for i, symbol in enumerate(syms):
            try:
                option_data = nseLive.equities_option_chain(symbol)
                options_data[symbol] = option_data
                quote_data = nseLive.stock_quote_fno(symbol)
                quotes_data[symbol] = quote_data
            except:
                print("couldn't fetch data for ", symbol, " at Index ", i)
                print("couldn't fetch data for symbol after", symbols[i-1])
                return False

    def find_put_ticks(expected_strike_price, option_data):
        nearest_expiry = option_data["records"]["expiryDates"][0]
        current_profitable_diff = 1000000
        current_losing_diff = -1000000
        option_ticks = ["", ""]

        for option in option_data["records"]["data"]:
            if "PE" in option.keys() and option["expiryDate"] == nearest_expiry:
                strike_price = option["strikePrice"]
                diff = strike_price - expected_strike_price
                if diff > 0 and diff < current_profitable_diff:
                    current_profitable_diff = diff
                    identifier = option["PE"]["identifier"]
                    option_ticks[0] = identifier

                if diff < 0 and diff > current_losing_diff:
                    current_losing_diff = diff
                    option_ticks[1] = option["PE"]["identifier"]
        return option_ticks

    def find_call_ticks(expected_strike_price, option_data):
        nearest_expiry = option_data["records"]["expiryDates"][0]
        current_losing_diff = 1000000
        current_profitable_diff = -1000000
        option_ticks = ["", ""]

        for option in option_data["records"]["data"]:
            if "CE" in option.keys() and option["expiryDate"] == nearest_expiry:
                strike_price = option["strikePrice"]
                diff = strike_price - expected_strike_price
                if diff < 0 and diff > current_profitable_diff:
                    current_profitable_diff = diff
                    identifier = option["CE"]["identifier"]
                    option_ticks[0] = identifier

                if diff > 0 and diff < current_losing_diff:
                    current_losing_diff = diff
                    option_ticks[1] = option["CE"]["identifier"]

        return option_ticks

    def find_quote(quote, tick):
        data = quote["stocks"]
        for q in data:
            if q["metadata"]["identifier"] == tick:
                return q

    def find_options(analysis_dict: Dict[str, OptionTradeAnalysisResult], option_type: str, tick_finder: Callable) -> List[Option]:
        options = []
        for symbol in analysis_dict.keys():
            current_option = options_data[symbol]
            current_quote = quotes_data[symbol]
            analysis = analysis_dict[symbol]
            underlying_value = current_option["records"]["underlyingValue"]
            expected_strike_price = underlying_value * (1 + analysis.change)

            [tick1, tick2] = tick_finder(expected_strike_price, current_option)
            if not tick1 or not tick2:
                continue

            quote1 = find_quote(current_quote, tick1)
            quote2 = find_quote(current_quote, tick2)

            expiry = datetime.strptime(
                        quote1["metadata"]["expiryDate"], "%d-%b-%Y"
                    )
            ltp1 = quote1["metadata"]["lastPrice"]
            ltp2 = quote2["metadata"]["lastPrice"]
            lot_size = quote1["marketDeptOrderBook"]["tradeInfo"]["marketLot"]
            options.append(
                Option(
                    symbol=symbol,
                    tick=tick1,
                    expiry=expiry,
                    strike=quote1["metadata"]["strikePrice"],
                    option_type=option_type,
                    lot_size=lot_size,
                    underlying_value=underlying_value,
                    current_price=ltp1 * lot_size,
                    initial_price=ltp1 * lot_size,
                    expected_hit=(datetime.today() + timedelta(days=analysis.days)).date(),
                    expected_change=analysis.change,
                )
            )
            options.append(
                Option(
                    symbol=symbol,
                    tick=tick2,
                    expiry=expiry,
                    strike=quote2["metadata"]["strikePrice"],
                    option_type=option_type,
                    lot_size=lot_size,
                    underlying_value=underlying_value,
                    current_price=ltp2 * lot_size,
                    initial_price=ltp2 * lot_size,
                    expected_hit=(
                        datetime.today() + timedelta(days=analysis.days)
                    ).date(),
                    expected_change=analysis.change,
                )
            )
        return options

    options = []
    options += find_options(put_high_analysis, "PUT", find_put_ticks)
    options += find_options(put_low_analysis, "PUT", find_put_ticks)
    options += find_options(call_high_analysis, "CALL", find_call_ticks)
    options += find_options(call_low_analysis, "CALL", find_call_ticks)

    options = [option for option in options if option.current_price > 0]
    options.sort(key=lambda x: x.expected_change, reverse=True)
    options_path = os.getenv("OPTIONS_PATH")

    if buy:
        portfolio = load_options_portfolio(options_path)
        risk = portfolio.cash_input * portfolio.risk
        options = [option for option in options if option.current_price <= risk]
        portfolio.add_options(options)
        option_path = Path(f"{options_path}/OptionPortfolio.json")

        with open(option_path, "w") as file:
            file.write(portfolio.model_dump_json(indent=4))

        return

    options = [option for option in options if option.current_price <= r]

    today = datetime.today().date()
    option_portfolio = OptionPortfolio(date=today, options=options)
    path = Path(f"{options_path}/{today}.json")

    with open(path,"w") as file:
        file.write(option_portfolio.model_dump_json(indent=4))
