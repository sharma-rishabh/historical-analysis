import pytest
import pandas as pd
from datetime import date
from invest_assist.strategies import FortyTwenty
from invest_assist.trade import Trade


columns = [
    "DATE",
    "LTP",
    "HIGH",
    "LOW",
    "OPEN",
]


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
    return pd.DataFrame(data, columns=columns)


@pytest.fixture()
def forty_twenty(df):
    return FortyTwenty(df=df)


class TestFortyTwenty:
    def test_preprocess(self, forty_twenty: FortyTwenty):
        expected_columns = [
            "index",
            "DATE",
            "LTP",
            "HIGH",
            "LOW",
            "OPEN",
            "40D_HIGH",
            "LOWEST_20D",
        ]

        expected_last_row = [
            99,
            date(2024, 2, 1),
            140,
            160,
            140,
            140,
            160,
            121,
        ]
        forty_twenty.preprocess()

        assert forty_twenty.df.columns.tolist() == expected_columns
        assert forty_twenty.df.iloc[-1].tolist() == expected_last_row

    def test_execute(self, forty_twenty: FortyTwenty):
        trade1 = Trade(
            buy_price=80, start_date=date(2024, 2, 1), initial_stop_loss=61.0
        )
        trade1.stop_loss = 80.0
        trade1.selling_price = 80.0
        trade1.selling_date = date(2024, 2, 1)

        trade2 = Trade(
            buy_price=101, start_date=date(2024, 2, 1), initial_stop_loss=80.0
        )
        trade2.stop_loss = 140
        trade2.selling_price = 140
        trade2.selling_date = date(2024, 2, 1)

        expected = [trade1, trade2]
        actual = forty_twenty.execute()
        
        assert actual == expected

    def test_get_stop_loss(self, forty_twenty: FortyTwenty):
        assert forty_twenty.get_stop_loss() == 121

    def test_breakout_true(self, forty_twenty: FortyTwenty):
        today = {
            "lastPrice": 150,
            "open": 150,
            "intraDayHighLow": {
                "max": 161,
                "min": 140
            }
        }

        assert forty_twenty.breakout(today) == True
    
    def test_breakout_empty_df(self, df: pd.DataFrame):
        today = {
            "lastPrice": 150,
            "open": 150,
            "intraDayHighLow": {
                "max": 161,
                "min": 140
            }
        }
        
        forty_twenty = FortyTwenty(df[:39])
        assert forty_twenty.breakout(today) == False
    
    def test_breakout_false(self, forty_twenty: FortyTwenty):
        today = {
            "lastPrice": 150,
            "open": 150,
            "intraDayHighLow": {
                "max": 159,
                "min": 140
            }
        }
        

        assert forty_twenty.breakout(today) == False