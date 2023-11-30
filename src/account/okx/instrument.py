from pydantic.dataclasses import dataclass
from datetime import datetime, timedelta

@dataclass
class Instrument():
    ccy: str = None
    instId: str = None
    day: int = None
    month: int = None
    year: int = None
    tte: float = None

    def __post_init__(self):
        opt_string = self.instId.split('-')
        date_now = datetime.utcnow()
        date_option = datetime.strptime(opt_string[2], '%y%m%d')
        date_option = date_option + timedelta(hours=8)
        date_delta = date_option-date_now
        self.ccy = opt_string[0]
        self.tte = date_delta.total_seconds() /60/60/24
        try:
            self.day = date_option.day
            self.month = date_option.month
            self.year = date_option.year
        except ValueError as e:
            raise e

def main():
    inst = Instrument({"BTC-USD-231124-39000-P"})
    print(inst)

if __name__ == '__main__':
    main()    