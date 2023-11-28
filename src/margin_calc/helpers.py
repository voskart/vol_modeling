from margin_calc.position import Position
from margin_calc.option import Option
from datetime import datetime
import statsmodels.api as sm
import numpy as np
import json


'''
Put-Call parity calculation. Two options with the same expiry and strike
Goal is approximation of r, the risk-free rate

TODO: Call OKX Api to get "most liquid" pair, as well as current idxPx
'''
def put_call_parity(put: Position = None, call: Position = None) -> float:
    # sample options
    call = Position({"adl": "5", "availPos": "100", "avgPx": "0.0055", "baseBal": "", "baseBorrowed": "", "baseInterest": "", "bePx": "", "bizRefId": "", "bizRefType": "", "cTime": "1698970571898", "ccy": "BTC", "closeOrderAlgo": [], "deltaBS": "-0.07944308303267127", "deltaPA": "-0.07652538277632571", "fee": "-0.00019", "fundingFee": "0", "gammaBS": "-5.117577574938401E-5", "gammaPA": "-1.6102515285129742", "idxPx": "36509.1", "imr": "3.038456133793251", "instId": "BTC-USD-231117-35000-C", "instType": "OPTION", "interest": "", "last": "0.0037", "lever": "", "liab": "", "liabCcy": "", "liqPenalty": "0", "liqPx": "", "margin": "", "markPx": "0.057", "mgnMode": "cross", "mgnRatio": "2.392771905957076", "mmr": "2.3372739490717316", "notionalUsd": "34457.1", "optVal": "0.07", "pendingCloseOrdLiabVal": "", "pnl": "0", "pos": "100", "posCcy": "", "posId": "640464230906789953", "posSide": "net", "quoteBal": "", "quoteBorrowed": "", "quoteInterest": "", "realizedPnl": "-0.00019", "sId": 0, "spotInUseAmt": "0", "spotInUseCcy": "BTC", "thetaBS": "33.64693204042858", "thetaPA": "9.504012377647234E-4", "tradeId": "15", "uTime": "1698970571898", "upl": "0.0025819530013177", "uplLastPx": "0.0018", "uplRatio": "0.4694460002395895", "uplRatioLastPx": "0.3272727272727272", "usdPx": "34457.1", "userId": 39471864, "vegaBS": "-6.811811024356156", "vegaPA": "-1.9769707928291187E-4", "markVol":"0"})
    put = Position({"adl": "5", "availPos": "100", "avgPx": "0.0055", "baseBal": "", "baseBorrowed": "", "baseInterest": "", "bePx": "", "bizRefId": "", "bizRefType": "", "cTime": "1698970571898", "ccy": "BTC", "closeOrderAlgo": [], "deltaBS": "-0.07944308303267127", "deltaPA": "-0.07652538277632571", "fee": "-0.00019", "fundingFee": "0", "gammaBS": "-5.117577574938401E-5", "gammaPA": "-1.6102515285129742", "idxPx": "36509.1", "imr": "3.038456133793251", "instId": "BTC-USD-231117-35000-P", "instType": "OPTION", "interest": "", "last": "0.0037", "lever": "", "liab": "", "liabCcy": "", "liqPenalty": "0", "liqPx": "", "margin": "", "markPx": "0.0126", "mgnMode": "cross", "mgnRatio": "2.392771905957076", "mmr": "2.3372739490717316", "notionalUsd": "34457.1", "optVal": "0.07", "pendingCloseOrdLiabVal": "", "pnl": "0", "pos": "100", "posCcy": "", "posId": "640464230906789953", "posSide": "net", "quoteBal": "", "quoteBorrowed": "", "quoteInterest": "", "realizedPnl": "-0.00019", "sId": 0, "spotInUseAmt": "0", "spotInUseCcy": "BTC", "thetaBS": "33.64693204042858", "thetaPA": "9.504012377647234E-4", "tradeId": "15", "uTime": "1698970571898", "upl": "0.0025819530013177", "uplLastPx": "0.0018", "uplRatio": "0.4694460002395895", "uplRatioLastPx": "0.3272727272727272", "usdPx": "34457.1", "userId": 39471864, "vegaBS": "-6.811811024356156", "vegaPA": "-1.9769707928291187E-4", "markVol":"0"})
    # expiry, strike, spot price
    assert call.tte == put.tte, "TTE not equal!"
    assert call.strike == put.strike, "Strikes not equal!"
    expiry = call.tte
    strike = call.strike
    spot = call.idxPx
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

