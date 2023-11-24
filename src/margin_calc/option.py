from pydantic.dataclasses import dataclass

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
        