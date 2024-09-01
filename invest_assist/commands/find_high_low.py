from datetime import datetime
import json
import math
import multiprocessing
from multiprocessing import shared_memory
import pickle
import click
import concurrent.futures
import numpy as np
import pandas as pd
from io import StringIO
from itertools import combinations
from invest_assist.CummulativeAnalyzer import CumulativeAnalyzer
from invest_assist.HighLowAnalyzer import HighLowAnalyzer
from invest_assist.company_list import listings
from invest_assist.strategies import FindHighLow
from .utils import get_historical_data



def get_analysis(stock_data, high, low):
    trades = FindHighLow(stock_data, high, low).execute()
    result =  HighLowAnalyzer(trades).analyze()
    return result


def analyze_combination(historical_data, high, low):
    results = {f"{high}-{low}": [], f"{low}-{high}": []}
    symbols = historical_data.keys()
    for symbol in symbols:
        stock_data = historical_data[symbol]
        result_high_low = get_analysis(stock_data, high, low)
        result_low_high = get_analysis(stock_data, low, high)
        results[f"{high}-{low}"].append(result_high_low)
        results[f"{low}-{high}"].append(result_low_high)
    return results


def merge_results(analysis, new_results):
    for key, value in new_results.items():
        analysis[key].extend(value)


def run_analysis_multithreaded(
    historical_data,
    high_low_combinations
):
    analysis = {}

    # Initialize the dictionary keys
    for high, low in high_low_combinations:
        analysis[f"{high}-{low}"] = []
        analysis[f"{low}-{high}"] = []

    with concurrent.futures.ProcessPoolExecutor(max_workers=100) as executor:
        future_to_combination = {
            executor.submit(analyze_combination, historical_data, high, low): (
                high,
                low,
            )
            for high, low in high_low_combinations
        }

        for future in concurrent.futures.as_completed(future_to_combination):
            high, low = future_to_combination[future]
            try:
                new_results = future.result()
                merge_results(analysis, new_results)
                print(f"Completed analysis for {high}-{low} and {low}-{high}")
            except Exception as e:
                print(f"Error analyzing {high}-{low} and {low}-{high}: {e.with_traceback()}")

    return analysis


@click.command()
@click.option("--all", is_flag=True, help="Run breakout against all stocks")
@click.option(
    "-n",
    type=int,
    required=False,
    default=50,
    help="Top n companies you want to check for.",
)
def find_high_low(n: int, all: bool):
    """Find high and low of n companies."""

    df = pd.read_csv(StringIO(listings))

    if all:
        n = len(df)

    symbols = df.head(n)["Symbol"].tolist()

    historical_data = {}


    with click.progressbar(symbols) as syms:
        for symbol in syms:
            try:
                stock_data = get_historical_data(symbol, 4000)
                historical_data[symbol] = stock_data
            except:
                return False



    with open("high_low_combinations.json", "r") as file:
        all_high_low_combinations = json.load(file)
        high_low_combinations = all_high_low_combinations[:100]

    with open("high_low_combinations.json", "w") as file:
        json.dump(all_high_low_combinations[100:], file)



    analysis = run_analysis_multithreaded(historical_data, high_low_combinations)

    # analysis = {}
    # for high, low in high_low_combinations:
    #     analysis[f"{high}-{low}"] = []
    #     analysis[f"{low}-{high}"] = []
    #     print(f"Running analysis for {high}-{low} and {low}-{high}")
    #     for symbol in historical_data.keys():
    #         stock_data = historical_data[symbol]
    #         result_high_low = get_analysis(stock_data, high, low)
    #         result_low_high = get_analysis(stock_data, low, high)
    #         analysis[f"{high}-{low}"].append(result_high_low)
    #         analysis[f"{low}-{high}"].append(result_low_high)

    print(f"TOTAL ANALYZED - {len(analysis.keys())}")
    results = []
    for key in analysis.keys():
        analyzer = CumulativeAnalyzer(analysis[key], key)
        results.append(analyzer.analyse())
        print(f"Completed analysis for {key}")


    result_dicts = [result.model_dump() for result in results]
    df = pd.DataFrame(result_dicts)


    df = df.sort_values(by="returns", ascending=False)
    df.drop_duplicates(subset=["type"], keep="first", inplace=True)
    with open("high_low_analysis.csv", "a") as file:
        file.write(df.to_csv(index=False, header=False))

    df[:1000]
    print(df.to_csv(index=False))
