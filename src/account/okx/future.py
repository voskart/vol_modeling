from pydantic.dataclasses import dataclass
from account.okx.instrument import Instrument

@dataclass
class Future(Instrument):
    markPx: float = None

def main():
    fut = {"instId": "BTC-USD-231229","instType": "FUTURES","markPx": "37676.9","ts": "1700682973370"}
    f = Future(**fut)
    print(f)

if __name__ == '__main__':
    main()