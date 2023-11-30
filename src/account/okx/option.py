from pydantic.dataclasses import dataclass
from account.okx.instrument import Instrument
from typing import Literal, Optional
from datetime import datetime, timedelta

@dataclass
class Option(Instrument):
    askVol: Optional[float] = None
    bidVol: Optional[float] = None
    delta: Optional[float] = None
    deltaBS: float = None
    fwdPx: Optional[float] = None
    gamma: Optional[float] = None
    gammaBS: float = None
    instId: str = None
    instType: str = None
    markVol: float = None
    realVol: Optional[float] = None
    theta: Optional[float] = None
    thetaBS: float = None
    ts: Optional[float] = None
    uly: Optional[str] = None 
    vega: Optional[float] = None
    vegaBS: float = None 
    volLv: Optional[float] = None
    markPx: float = None
    type: Literal['c', 'p'] = None
    strike: int = None
    pos: int = 100
    markVol: float = 0.0
    idxPx: Optional[float] = None

    def __post_init__(self):
        super().__post_init__() 
        opt_string = self.instId.split('-')
        self.strike = int(opt_string[3])
        self.type = opt_string[4].lower()

def main():
    opt = {
        "askVol": "1.771246691894531",
        "bidVol": "0.8984457031249999",
        "delta": "-0.00546371558658575",
        "deltaBS": "-0.003916242212059047",
        "fwdPx": "39069.2370763525319",
        "gamma": "0.02330281859983678",
        "gammaBS": "0.00000033210034957775",
        "instId": "BTC-USD-240628-5000-P",
        "instType": "OPTION",
        "lever": "646.2146725502389",
        "markVol": "1.2168943116801167",
        "realVol": "0",
        "theta": "-0.00002509217880720357",
        "thetaBS": "-0.8907202180143806",
        "ts": "1700777423853",
        "uly": "BTC-USD",
        "vega": "0.00008970098868943831",
        "vegaBS": "3.342617642523229",
        "volLv": "0.6115263820391076",
        "markPx": "0.001547475434125"
    }

    o = Option(**opt)
    print(o)

if __name__ == '__main__':
    main()
    

    
        