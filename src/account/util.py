from datetime import datetime, timedelta
from account.account import BaseAccount
from account.okx.option import Option
import statsmodels.api as sm
import math
import json
import numpy as np

def find_closest_expiry(acc: BaseAccount, tte):
        # expiration in tte
        wanted_expiration = datetime.now() + timedelta(days=tte)
        delta_expiration = math.inf
        closest_expiration = ''
        if not acc.market_data_options:
            raise RuntimeError('Option data has not been collected yet, re-run')
        for inst in acc.market_data_options:
            # get expiration from instId
            options_expiration_str = inst.instId.split('-')[2]
            expiration_cur = datetime.strptime(options_expiration_str, '%y%m%d')
            cur_delta = expiration_cur-wanted_expiration
            if abs(cur_delta.days) < delta_expiration:
                delta_expiration = abs(cur_delta.days)
                closest_expiration = options_expiration_str
        return closest_expiration

# TODO: Create two sets (calls, puts) and order by delta
def find_contract(acc: BaseAccount, type, expiry: str, delta):
    delta_closest = math.inf
    closest_contract = None
    for inst in acc.market_data_options:
        # TODO: add call/put field to Option class
        if expiry in inst.instId and inst.instId.split('-')[4].lower() == type:
            if abs(abs(inst.delta)-delta) < delta_closest:
                closest_contract = inst
                delta_closest = abs(abs(inst.delta)-delta)
    return closest_contract

def find_contract_by_strike_exp(acc: BaseAccount, type, expiry: str, strike: int):
    for inst in acc.market_data_options:
            if expiry in inst.instId and inst.instId.split('-')[4].lower() == type and inst.strike == strike:
                return inst
            
'''
Put-Call parity calculation. Two options with the same expiry and strike
Goal is approximation of r, the risk-free rate

TODO: Call OKX Api to get "most liquid" pair, as well as current idxPx
'''
def put_call_parity(acc: BaseAccount, put: Option = None, call: Option = None, spot: float = 0) -> float:
    # sample options 
    call = find_contract_by_strike_exp(acc, 'c', '240329', 35000)
    put = find_contract_by_strike_exp(acc, 'p', '240329', 35000)
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

