import unittest
from unittest.mock import patch
import pytest
from datetime import date
from invest_assist.models.portfolio import HistoricalAnalysisResult, Holding, Portfolio


@pytest.fixture()
def historical_analysis_result():
    return HistoricalAnalysisResult(
        symbol="RELIANCE",
        returns=1.5,
        days_per_return=40,
        total_trades=33,
        winning_percentage=0.45,
    )


@pytest.fixture()
def holding(historical_analysis_result: HistoricalAnalysisResult):
    return Holding(
        id=1,
        symbol="RELIANCE",
        units=4,
        current_price=340,
        buying_price=330,
        stop_loss=300,
        strategy="FortyTwenty",
        buying_date=date(2024, 5, 1),
        sold=False,
        risk=200,
        historical_data=historical_analysis_result,
    )


@pytest.fixture()
def holding_id_2(historical_analysis_result: HistoricalAnalysisResult):
    return Holding(
        id=2,
        symbol="GCPOWER",
        units=4,
        current_price=250,
        buying_price=150,
        stop_loss=220,
        strategy="FortyTwenty",
        buying_date=date(2024, 5, 1),
        sold=False,
        risk=100,
        historical_data=historical_analysis_result,
    )


@pytest.fixture()
def portfolio(holding: Holding):
    return Portfolio(current_id=1, capital=3000, risk_percent=0.1, holdings=[holding])


class TestHolding:
    def test_update_stop_loss(self, holding: Holding):
        is_stop_loss_updated = holding.update_stop_loss(300.5)
        assert holding.stop_loss == 300.5
        assert is_stop_loss_updated == True

    def test_update_stop_loss_with_same_value(self, holding: Holding):
        is_stop_loss_updated = holding.update_stop_loss(300)
        assert holding.stop_loss == 300
        assert is_stop_loss_updated == False

    def test_update_risk(self, holding: Holding):
        is_current_price_updated = holding.update_current_price(350)
        assert holding.current_price == 350
        assert is_current_price_updated == True

    def test_sell(self, holding: Holding):
        selling_price = holding.sell(350)
        assert holding.sold == True
        assert holding.selling_date == date.today()
        assert holding.selling_price == 350
        assert selling_price == 350

    def test_sell_without_selling_price(self, holding: Holding):
        selling_price = holding.sell()
        assert holding.sold == True
        assert holding.selling_date == date.today()
        assert holding.selling_price == holding.stop_loss
        assert selling_price == holding.stop_loss

    def test_returns(self, holding: Holding):
        returns = holding.returns()
        assert returns == 40

    def test_returns_after_selling(self, holding: Holding):
        holding.sell()
        returns = holding.returns()
        assert returns == -120

    def test_returns_on_risk(self, holding: Holding):
        ror = holding.returns_on_risk()
        assert ror == 0.2


class TestPortfolio:
    def test_update_risk(self, portfolio: Portfolio):
        updated_risk = portfolio.update_risk(0.05)
        assert portfolio.risk_percent == updated_risk == 0.05

    def test_update_capital(self, portfolio: Portfolio):
        updated_capital = portfolio.update_capital(300)
        assert portfolio.capital == updated_capital == 3300

    def test_update_negative_capital(self, portfolio: Portfolio):
        updated_capital = portfolio.update_capital(-300)
        assert portfolio.capital == updated_capital == 2700

    def test_find_by_id(
        self, portfolio: Portfolio, holding: Holding, holding_id_2: Holding
    ):
        portfolio.holdings.append(holding_id_2)
        assert portfolio.find_by_id(1) == holding
        assert portfolio.find_by_id(2) == holding_id_2

    def test_find_by_symbol(
        self, portfolio: Portfolio, holding: Holding, holding_id_2: Holding
    ):

        holding_id_2.symbol = holding.symbol
        portfolio.holdings.append(holding_id_2)

        assert portfolio.find_by_symbol(holding.symbol) == [holding, holding_id_2]

    def test_sell_by_symbol(
        self, portfolio: Portfolio, holding: Holding, holding_id_2: Holding
    ):
        holding_id_2.symbol = holding.symbol
        portfolio.holdings.append(holding_id_2)

        sold_for = portfolio.sell_by_symbol(holding.symbol, None)
        assert sold_for == holding_id_2.stop_loss
        assert portfolio.capital == 3160

    def test_sell_by_id(
        self, portfolio: Portfolio, holding: Holding, holding_id_2: Holding
    ):
        portfolio.holdings.append(holding_id_2)

        sold_for = portfolio.sell_by_id(2, None)
        assert sold_for == holding_id_2.stop_loss
        assert portfolio.capital == 3280

    def test_get_next_id(self, portfolio: Portfolio):
        next_id = portfolio.get_next_id()
        assert next_id == portfolio.current_id == 2

    def test_active_stocks(self, portfolio: Portfolio, holding_id_2: Holding):
        portfolio.holdings.append(holding_id_2)
        portfolio.sell_holdings(1, None, None)

        stocks = portfolio.active_stocks()
        assert stocks == [holding_id_2]

    def test_invested(self, portfolio: Portfolio, holding_id_2: Holding):
        portfolio.holdings.append(holding_id_2)

        assert portfolio.invested() == 1920

    def test_current_value(self, portfolio: Portfolio, holding_id_2: Holding):
        portfolio.holdings.append(holding_id_2)

        assert portfolio.current_value() == 2360

    def test_remaining_capital(self, portfolio: Portfolio):
        assert portfolio.remaining_capital() == 1680

    def test_return_percent(self, portfolio: Portfolio):
        assert round(portfolio.return_percent(), 3) == 0.013

    def test_cash_flows(self, portfolio: Portfolio, holding_id_2: Holding):
        portfolio.holdings.append(holding_id_2)
        portfolio.sell_holdings(1, None, None)
        portfolio.sell_holdings(2, None, 250.0)

        portfolio.holdings[0].selling_date = date(2024, 8, 1)
        portfolio.holdings[1].buying_date = date(2024, 4, 1)
        portfolio.holdings[1].selling_date = date(2024, 5, 1)
        print(portfolio.holdings)
        expected = [
            (-1320.0, date(2024, 5, 1)),
            (1200.0, date(2024, 8, 1)),
            (-600.0, date(2024, 4, 1)),
            (1000.0, date(2024, 5, 1)),
        ]

        assert portfolio.cash_flows() == expected

    def test_xirr(self, portfolio: Portfolio, holding_id_2: Holding):
        portfolio.holdings.append(holding_id_2)
        portfolio.sell_holdings(1, None, None)
        portfolio.sell_holdings(2, None, 250.0)

        portfolio.holdings[0].selling_date = date(2024, 8, 1)
        portfolio.holdings[1].buying_date = date(2024, 4, 1)
        portfolio.holdings[1].selling_date = date(2024, 5, 1)

        assert portfolio.xirr() == 138.07

    def test_get_units_cost_greater_than_investment(self, portfolio: Portfolio):
        assert portfolio.get_units(1200, 250, 200) == 4

    def test_get_units_cost_less_than_investment(self, portfolio: Portfolio):
        assert portfolio.get_units(1500, 250, 200) == 6

    def test_risk(self, portfolio: Portfolio):
        assert portfolio.get_risk(6, 250, 200) == 300

    def test_buy_stock_zero_units(
        self, portfolio: Portfolio, historical_analysis_result: HistoricalAnalysisResult
    ):
        expected = Holding(
            symbol="REL",
            units=0,
            current_price=3000,
            buying_price=3000,
            stop_loss=2800,
            strategy="FortyTwenty",
            buying_date=date(2024, 5, 1),
            historical_data=historical_analysis_result,
            risk=0,
            sold=False,
        )

        actual = portfolio.buy_stock(
            symbol="REL",
            current_price=3000,
            buying_price=3000,
            stop_loss=2800,
            buying_capacity=1,
            strategy="FortyTwenty",
            buying_date=date(2024, 5, 1),
            hd=historical_analysis_result,
            info_only=False,
        )

        assert actual == expected

    def test_buy_stock_info_only(
        self, portfolio: Portfolio, historical_analysis_result: HistoricalAnalysisResult
    ):
        expected = Holding(
            symbol="REL",
            units=5,
            current_price=300,
            buying_price=300,
            stop_loss=280,
            strategy="FortyTwenty",
            buying_date=date(2024, 5, 1),
            historical_data=historical_analysis_result,
            risk=100,
            sold=False,
        )

        actual = portfolio.buy_stock(
            symbol="REL",
            current_price=300,
            buying_price=300,
            stop_loss=280,
            buying_capacity=1,
            strategy="FortyTwenty",
            buying_date=date(2024, 5, 1),
            hd=historical_analysis_result,
            info_only=True,
        )

        assert actual == expected

    def test_buy_stock(
        self, portfolio: Portfolio, historical_analysis_result: HistoricalAnalysisResult
    ):
        expected = Holding(
            id=2,
            symbol="REL",
            units=5,
            current_price=300,
            buying_price=300,
            stop_loss=280,
            strategy="FortyTwenty",
            buying_date=date(2024, 5, 1),
            historical_data=historical_analysis_result,
            risk=100,
            sold=False,
        )

        actual = portfolio.buy_stock(
            symbol="REL",
            current_price=300,
            buying_price=300,
            stop_loss=280,
            buying_capacity=1,
            strategy="FortyTwenty",
            buying_date=date(2024, 5, 1),
            hd=historical_analysis_result,
            info_only=False,
        )

        assert actual == expected
