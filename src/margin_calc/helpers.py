from margin_calc.position import Position
from margin_calc.option import Option
from margin_calc.okx_account import OKXAccount
from datetime import datetime
import statsmodels.api as sm
import numpy as np
import json


'''
Put-Call parity calculation. Two options with the same expiry and strike
Goal is approximation of r, the risk-free rate

TODO: Call OKX Api to get "most liquid" pair, as well as current idxPx
'''
def put_call_parity(put: Position = None, call: Position = None, spot: float = 0) -> float:
    # sample options
    ok = OKXAccount() 
    call = ok.find_contract_by_strike_exp('c', '240329', 35000)
    put = ok.find_contract_by_strike_exp('p', '240329', 35000)
    # expiry, strike, spot price
    assert call.tte == put.tte, "TTE not equal!"
    assert call.strike == put.strike, "Strikes not equal!"
    expiry = call.tte
    strike = call.strike
    # formula: c+Ke**-rT = p+Se**(-qT), looking for r
    r = -np.log((put.markPx-call.markPx+spot)/(strike))/(expiry/365)
    return r/100

def linear_approximation(ivs: [int], tte: [int], range: [int]) -> [float]:
    assert len(ivs) == len(tte), "Length not equal!"
    # we are predicting ivs based on tte
    x = tte
    y = ivs
    x = sm.add_constant(x)
    range = sm.add_constant(range)
    lm = sm.OLS(y,x).fit()
    predict = lm.predict(range)
    return predict

def get_calls(n=5) -> None:
    calls = []
    try:
        with open('./data/vega_risk.json') as f:
            for call in json.load(f):
                date_str = call['instId'].split('-')
                delta = datetime.strptime(date_str[2], "%y%m%d") - datetime.now() 
                call['expiration_days'] = delta.days
                call['strike'] = date_str[3]
                calls.append(call)
        return calls
    except:
        raise Exception
    
def short_option(opt: Option):
    opt.deltaBS *= -1
    opt.gammaBS *= -1
    opt.thetaBS *= -1
    opt.vegaBS *= -1
    opt.pos *= -1

def main():
    print(linear_approximation([50,35,25], [0, 30, 90], range))

if __name__ == "__main__":
    main()

