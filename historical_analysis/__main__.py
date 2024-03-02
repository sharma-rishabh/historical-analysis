from datetime import date, timedelta
import json
from jugaad_data.nse import stock_df
import pandas as pd
from cumulative_analysis_result import CumulativeAnalysisResult
from strategies.forty_twenty import FortyTwenty
from analyzer import Analyzer
from risk_profile import RiskProfile



def format_result(
    symbol: str, strategy_name: str, cumulative_results: CumulativeAnalysisResult
):
    result = f"{symbol} with {strategy_name}\n"
    result += f"Average return on risk: {cumulative_results.average_return_on_risk} \n"

    result += f"Average days taken: {cumulative_results.average_days} \n"
    result += f"Profitable Trades: {round(cumulative_results.profitable_trades * 100, 2)}% \n"
    result += f"Profitable trade returns: {cumulative_results.average_profit_return} \n"
    result += f"Loss Making Trades: {round(cumulative_results.loss_making_trades * 100, 2)}% \n"
    result += f"Loss Making trade returns: {cumulative_results.average_loss_return}\n"
    return result


strategy_class = {
    "FortyTwenty": FortyTwenty,
}


def get_historical_data(symbol: str, years: int) -> pd.DataFrame:
    today = date.today()
    ten_years_ago = today - timedelta(days=365 * years)
    df = stock_df(symbol=symbol, from_date=ten_years_ago, to_date=today, series="EQ")

    df = df.drop_duplicates()
    return df


def main():
    with open('data.json','r') as file:
        data = json.load(file)
        
    capital = data['capital']
    risk = data['risk']
    raw_strategies = data['strategies']
    symbols = data['symbols']
    years = data['years']

    stock_data = [get_historical_data(symbol, years) for symbol in symbols]
    strategies = [strategy_class[name] for name in raw_strategies]
    profile = RiskProfile(capital, risk)

    for symbol, data in zip(symbols, stock_data):
        trades_per_strategy = [strategy(data).execute() for strategy in strategies]

        results = [
            Analyzer(trades, profile).analyse() for trades in trades_per_strategy
        ]

        [
            print(format_result(symbol, strategy_name, result))
            for result, strategy_name in zip(results, raw_strategies)
        ]

main()
