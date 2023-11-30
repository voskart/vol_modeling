from pydantic.dataclasses import dataclass
from typing import Literal
from datetime import datetime, timedelta

@dataclass
class Option:
    askVol: float = None
    bidVol: float = None
    delta: float = None
    deltaBS: float = None
    fwdPx: float = None
    gamma: float = None
    gammaBS: float = None
    instId: str = None
    instType: str = None
    lever: float = None
    markVol: float = None
    realVol: float = None
    theta: float = None
    thetaBS: float = None
    ts: int = None
    uly: str = None 
    vega: float = None
    vegaBS: float = None 
    volLv: float = None
    markPx: float = None
    type: Literal['c', 'p'] = None
    strike: int = None
    tte: int = None
    pos: int = 100

    def __post_init__(self):
        # "BTC-USD-240628-5000-P"
        opt_string = self.instId.split('-')
        date_now = datetime.utcnow()
        date_option = datetime.strptime(opt_string[2], '%y%m%d')
        date_option = date_option + timedelta(hours=8)
        date_delta = date_option-date_now
        self.strike = int(opt_string[3])
        self.type = opt_string[4].lower()
        self.tte = date_delta.total_seconds() /60/60/24