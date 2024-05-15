from datetime import datetime


class Trade:
    def __init__(self, buy_price: int, start_date: datetime, initial_stop_loss: int):
        self.initial_stop_loss = initial_stop_loss
        self.buy_price = buy_price
        self.stop_loss = initial_stop_loss
        self.start_date = start_date
        self.selling_price = None
        self.selling_date = None

    def is_closed(self) -> bool:
        return self.selling_date != None

    def update_stop_loss(self, new_stop_loss: int) -> int:
        self.stop_loss = new_stop_loss
        return self.stop_loss

    def sell(self, selling_date: datetime) -> bool:
        self.selling_price = self.stop_loss
        self.selling_date = selling_date
        return True

    def __str__(self) -> str:
        return f"Trade(initial_stop_loss={self.initial_stop_loss}, buy_price={self.buy_price}, stop_loss={self.stop_loss}, start_date={self.start_date}, selling_price={self.selling_price}, selling_date={self.selling_date})"

    def __eq__(self, value: object) -> bool:
        if not isinstance(value, Trade):
            return False

        return (
            value.buy_price == self.buy_price
            and value.initial_stop_loss == self.initial_stop_loss
            and value.start_date == self.start_date
            and value.stop_loss == self.stop_loss
            and value.selling_price == self.selling_price
            and value.selling_date == self.selling_date
        )
