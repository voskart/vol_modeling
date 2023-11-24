from pydantic.dataclasses import dataclass
from datetime import datetime

@dataclass
class Instrument():
    instId: str = None
    day: int = None
    month: int = None
    year: int = None

    def __post_init__(self):
        inst_str = self.instId.split('-')
        inst_date = datetime.strptime(inst_str[2], '%y%m%d')
        try:
            self.day = inst_date.day
            self.month = inst_date.month
            self.year = inst_date.year
        except ValueError as e:
            raise e

def main():
    inst = Instrument("BTC-USD-231124-39000-P")
    print(inst)

if __name__ == '__main__':
    main()    