from datetime import date, datetime, timedelta
from typing import List
from unittest.mock import Mock
import pandas as pd
import pytest


from invest_assist.analyzer import Analyzer
from invest_assist.models.portfolio import Portfolio
from invest_assist.strategies.forty_twenty import FortyTwenty
from invest_assist.trade import Trade
from invest_assist.trade_analysis import TradeAnalysis


@pytest.fixture()
def portfolio():
    return Portfolio(current_id=0, capital=10000, risk_percent=0.1, holdings=[])


@pytest.fixture()
def data():
    def get_row(i):
        curr_date = date(2024, 2, 1)
        if i == 40:
            ltp = 110
            high = 120
            low = 80
            open = 100
            return [curr_date, ltp, high, low, open]

        ltp = 140 - i
        high = 160 - i
        low = 140 - i
        open = 140 - i
        return [curr_date, ltp, high, low, open]

    return [get_row(i) for i in range(100)]


@pytest.fixture()
def df(data):
    columns = [
        "DATE",
        "LTP",
        "HIGH",
        "LOW",
        "OPEN",
    ]
    return pd.DataFrame(data, columns=columns).drop_duplicates()


class MockStrategy:
    def __init__(self, historical_data) -> None:
        self.historical_data = historical_data
        self.trades = []

    def mock_trades(self, trades: List[Trade]):
        self.trades = trades

    def execute(self):
        return self.trades


class TestAnalyzer:
    def test_get_historical_data(
        self,
        portfolio: Portfolio,
        df: pd.DataFrame,
    ):
        stock_data = Mock()
        stock_data.return_value = df
        analyzer = Analyzer("REL", portfolio, FortyTwenty, 365, stock_data)
        today = date.today()

        analyzer.get_historical_data()
        stock_data.assert_called_once_with(
            symbol="REL",
            from_date=today - timedelta(days=365),
            to_date=today,
            series="EQ",
        )

    def test_get_trades(self, portfolio: Portfolio, df: pd.DataFrame):
        stock_data = Mock()
        stock_data.return_value = df

        analyzer = Analyzer("REL", portfolio, MockStrategy, 365, stock_data)

        assert analyzer.get_trades() == []

    def test_risk(self, portfolio: Portfolio, df: pd.DataFrame):
        stock_data = Mock()
        stock_data.return_value = df

        analyzer = Analyzer("REL", portfolio, MockStrategy, 365, stock_data)
        assert analyzer.risk() == 1000

    def test_overall_return(self, portfolio: Portfolio, df: pd.DataFrame):
        stock_data = Mock()
        stock_data.return_value = df

        analyzer = Analyzer("REL", portfolio, MockStrategy, 365, stock_data)
        assert analyzer.overall_return(10, 100, 110) == 100

    def test_get_units(self, portfolio: Portfolio, df: pd.DataFrame):
        stock_data = Mock()
        stock_data.return_value = df

        analyzer = Analyzer("REL", portfolio, MockStrategy, 365, stock_data)
        trade = Trade(
            buy_price=100,
            initial_stop_loss=90,
            start_date=date.today(),
        )
        assert analyzer.get_units(trade) == 100

    def test_get_units_with_less_capital(self, portfolio: Portfolio, df: pd.DataFrame):
        stock_data = Mock()
        stock_data.return_value = df

        analyzer = Analyzer("REL", portfolio, MockStrategy, 365, stock_data)
        trade = Trade(
            buy_price=100,
            initial_stop_loss=90,
            start_date=date.today(),
        )
        portfolio.capital = 500
        assert analyzer.get_units(trade) == 5

    def test_get_trade_analysis(self, portfolio: Portfolio, df: pd.DataFrame):
        stock_data = Mock()
        stock_data.return_value = df

        portfolio.capital = 500
        analyzer = Analyzer("REL", portfolio, MockStrategy, 365, stock_data)
        trade = Trade(
            buy_price=100,
            initial_stop_loss=90,
            start_date=date.today(),
        )

        trade.selling_price = 110
        trade.selling_date = date.today()

        assert analyzer.get_trade_analysis(trade) == TradeAnalysis(
            buying_price=100,
            selling_price=110,
            risk=50,
            return_on_risk=1.0,
            days=0,
            units=5,
            overall_returns=50,
        )

    def test_get_trade_analysis_with_no_risk(
        self, portfolio: Portfolio, df: pd.DataFrame
    ):
        stock_data = Mock()
        stock_data.return_value = df

        portfolio.capital = 500
        analyzer = Analyzer("REL", portfolio, MockStrategy, 365, stock_data)
        trade = Trade(
            buy_price=600,
            initial_stop_loss=90,
            start_date=date.today(),
        )

        trade.selling_price = 100
        trade.selling_date = date.today()

        assert analyzer.get_trade_analysis(trade) == TradeAnalysis(
            buying_price=0,
            selling_price=0,
            risk=0,
            return_on_risk=0,
            days=0,
            units=0,
            overall_returns=0,
        )

    def test_get_average_returns(self, portfolio: Portfolio, df: pd.DataFrame):
        stock_data = Mock()
        stock_data.return_value = df

        portfolio.capital = 500
        analyzer = Analyzer("REL", portfolio, MockStrategy, 365, stock_data)
        trade1 = TradeAnalysis(
            buying_price=100,
            selling_price=110,
            risk=50,
            return_on_risk=1.0,
            days=0,
            units=5,
            overall_returns=50,
        )

        trade2 = TradeAnalysis(
            buying_price=100,
            selling_price=120,
            risk=50,
            return_on_risk=2.0,
            days=0,
            units=5,
            overall_returns=100,
        )

        assert analyzer.avg_return([trade1, trade2]) == 1.5

    def test_avg_returns_empty_trade_analysis(
        self, portfolio: Portfolio, df: pd.DataFrame
    ):
        stock_data = Mock()
        stock_data.return_value = df

        portfolio.capital = 500
        analyzer = Analyzer("REL", portfolio, MockStrategy, 365, stock_data)
        assert analyzer.avg_return([]) == 0

    def test_get_average_days(self, portfolio: Portfolio, df: pd.DataFrame):
        stock_data = Mock()
        stock_data.return_value = df

        portfolio.capital = 500
        analyzer = Analyzer("REL", portfolio, MockStrategy, 365, stock_data)
        trade1 = TradeAnalysis(
            buying_price=100,
            selling_price=110,
            risk=50,
            return_on_risk=1.0,
            days=10,
            units=5,
            overall_returns=50,
        )

        trade2 = TradeAnalysis(
            buying_price=100,
            selling_price=120,
            risk=50,
            return_on_risk=2.0,
            days=20,
            units=5,
            overall_returns=100,
        )

        assert analyzer.avg_days([trade1, trade2]) == 15

    def test_avg_days_empty_trade_analysis(
        self, portfolio: Portfolio, df: pd.DataFrame
    ):
        stock_data = Mock()
        stock_data.return_value = df

        portfolio.capital = 500
        analyzer = Analyzer("REL", portfolio, MockStrategy, 365, stock_data)
        assert analyzer.avg_days([]) == 0

    def test_profitable_trades(self, portfolio: Portfolio, df: pd.DataFrame):
        stock_data = Mock()
        stock_data.return_value = df

        portfolio.capital = 500
        analyzer = Analyzer("REL", portfolio, MockStrategy, 365, stock_data)

        trade1 = TradeAnalysis(
            buying_price=100,
            selling_price=110,
            risk=50,
            return_on_risk=-1.0,
            days=10,
            units=5,
            overall_returns=50,
        )

        trade2 = TradeAnalysis(
            buying_price=100,
            selling_price=120,
            risk=50,
            return_on_risk=2.0,
            days=20,
            units=5,
            overall_returns=100,
        )

        assert analyzer.profitable_trades([trade1, trade2]) == [trade2]

    def test_analyse(self, portfolio: Portfolio, df: pd.DataFrame):
        stock_data = Mock()
        stock_data.return_value = df

        portfolio.capital = 500
        analyzer = Analyzer("REL", portfolio, MockStrategy, 365, stock_data)

        trade1 = Trade(
            buy_price=100,
            initial_stop_loss=90,
            start_date=date.today(),
        )
        trade1.selling_price = 110
        trade1.selling_date = date.today()

        trade2 = Trade(
            buy_price=200,
            initial_stop_loss=180,
            start_date=date.today(),
        )
        trade2.selling_price = 220
        trade2.selling_date = date.today()

        trade3 = Trade(
            buy_price=300,
            initial_stop_loss=270,
            start_date=date.today(),
        )
        trade3.selling_price = 270
        trade3.selling_date = date.today()

        analyzer.get_trades = Mock(return_value=[trade1, trade2, trade3])

        result = analyzer.analyse()

        assert result.symbol == "REL"
        assert result.returns == 0.33
        assert result.days_per_return == 0
        assert result.winning_percentage == 0.67
        assert result.total_trades == 3
