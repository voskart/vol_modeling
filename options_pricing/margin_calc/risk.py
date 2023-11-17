from position import Position
from okx_account import OKXAccount
from model import black_scholes
from helpers import put_call_parity, linear_approximation
import math
import numpy as np

class Risk:

    def __init__(self, positions: list[Position]) -> None:
        self.positions = positions
        self.positions_value = self.calculate_portfolio_value()

    def calculate_portfolio_value(self):
        cur_val = 0
        for pos in self.positions:
            cur_val += abs(pos.optVal)
        return cur_val

    '''
    Calculates spot shock scenarios based on OKX documentation at 0, 5, 10 and 15% and 0, 30 and 60 days to exp
    '''
    def spot_shock(self) -> float:
        spot_move_pct = [0, -5, 5, -10, 10, -15, 15]
        # point change in IV, 30 would result in a change from 50% to 80% (0, 30 and 60 days respectively)
        iv_change_pct = [50, 35, 25]
        idx_price = self.positions[0].idxPx
        min_val = self.positions_value
        r = put_call_parity()
        # for all combinations, calculate new option prices and corresponding portfolio value
        for s in spot_move_pct:
            for iv_change in iv_change_pct:
                # iterate through portfolio and update pricing
                # setting spot price, and iv
                # set mark iv for each contract
                tmp = 0
                for pos in self.positions:
                    # change in spot price as well as change in IV
                    iv = 0.58
                    b = black_scholes(idx_price*(1+s/100), pos.strike, r, iv*(1+iv_change/100), pos.expiration_days/365, pos.type.lower())/idx_price*pos.pos/100
                    tmp += b
                min_val = min(tmp, min_val)
        return self.positions_value-min_val

    '''
    Calculates the theta decay for a 24h period
    '''
    def time_decay(self) -> float:
        theta_decay = 0
        for pos in self.positions:
            theta_decay += pos.theta
        return theta_decay
    
    # tbd what "It measures the risk of change in implied volatility across different expiry dates that is not captured in MR1." means exactly
    def vega_risk(self):
        # initial iv change percent for 0, 30 and 60 days
        tte = [0, 30, 60]
        initial_iv_change_pct = [50, 35, 25]
        # expiry_dates = np.arange(1,90)
        # linear approximation for above expiries
        # iv_values = linear_approximation(initial_iv_change_pct, tte, expiry_dates)
        expiry_dates = [1,2,3]
        iv_change_pct = [48,47,45]
        iv_dict = dict(zip(expiry_dates, iv_change_pct))
        min_val = self.positions_value
        idx_price = self.positions[0].idxPx
        r = put_call_parity()
        # for each option, calculate the minimum value for a contract while changing tte and iv, then compare to initial contract
        vega_risk = 0
        for pos in self.positions:
            iv = 0.60
            # calculate deltas for each contract with different expiry dates
            # for each contract, calculate prices for tte 1-90 and corresponding iv change
            # calculate maximum loss for each position simulation
            
            # calculates max loss for current expiry with varying iv shocks
            max_loss_current = math.inf
            for i in iv_change_pct:
                b = black_scholes(idx_price, pos.strike, r, iv*1+i/100, pos.expiration_days/365, pos.type.lower())/idx_price*abs(pos.pos/100)
                max_loss_current = min(max_loss_current, abs(pos.optVal-b))

            # calculates max loss by changing expiries and iv shocks
            max_loss = math.inf
            for e in expiry_dates:
                opt_val = black_scholes(idx_price, pos.strike, r, iv*1/100, e/365, pos.type.lower())/idx_price*abs(pos.pos/100)
                for i in iv_change_pct:
                    b = black_scholes(idx_price, pos.strike, r, iv*1+i/100, e/365, pos.type.lower())/idx_price*abs(pos.pos/100)
                    max_loss = min(max_loss, abs(opt_val-b))
            
            print(max_loss_current, max_loss)
            vega_risk += abs(max_loss_current - max_loss)    

        return vega_risk


    def basis_risk():
        raise NotImplemented
    
    '''
    Calculates the risk in the case of changes in interest rates by populating a PCA rate movement table
    TODO: model full-on yield curve 
    '''
    def interest_rate_risk():
        # parallel shift
        pc1 = [3, 2, 1.75, 1.5, 1, 0.9, 0.8, 0.7]
        # slope change
        pc2 = [4, 3, 2, 1, 0, -0.5, -0.75, -0.9]
        pc1_pct = [5, -5, 2.5, -2.5, 2, -2]
        pc2_pct = [3, -3]
        # need to get yield for 1 day to 720 days out and then shift the curve accordingly

    '''
    Calculates the risk in case the underlying experiences a large move. Contrary to spot_shock, IV remains unchanged
    MR of a risk unit is half of the maximum loss when BTC-USD moves +30% or -30%, whichever is larger
    '''
    def extreme_move(self) -> float:
        spot_move_pct = [-30, 30]
        idx_price = self.positions[0].idxPx
        r = put_call_parity()
        
        min_val = self.positions_value
        for s in spot_move_pct:
            for pos in self.positions:
                # set mark iv for each contract
                iv = 0.81 if pos.type == 'P' else 0.57
                # change in spot price
                b = black_scholes(idx_price*(1+s/100), pos.strike, r, iv, pos.expiration_days/365, pos.type.lower())/idx_price*abs(pos.pos/100)
                min_val = min(b, min_val)
        return (self.positions_value-min_val)/2
    
    def minimum_charge():
        raise NotImplemented
    
if __name__ == '__main__':
    ok = OKXAccount()
    # positions = [Position({"adl": "5", "availPos": "100", "avgPx": "0.0055", "baseBal": "", "baseBorrowed": "", "baseInterest": "", "bePx": "", "bizRefId": "", "bizRefType": "", "cTime": "1698970571898", "ccy": "BTC", "closeOrderAlgo": [], "deltaBS": "-0.07944308303267127", "deltaPA": "-0.07652538277632571", "fee": "-0.00019", "fundingFee": "0", "gammaBS": "-5.117577574938401E-5", "gammaPA": "-1.6102515285129742", "idxPx": "36200.1", "imr": "3.038456133793251", "instId": "BTC-USD-231117-38000-C", "instType": "OPTION", "interest": "", "last": "0.0037", "lever": "", "liab": "", "liabCcy": "", "liqPenalty": "0", "liqPx": "", "margin": "", "markPx": "0.0192", "mgnMode": "cross", "mgnRatio": "2.392771905957076", "mmr": "2.3372739490717316", "notionalUsd": "34457.1", "optVal": "0.07", "pendingCloseOrdLiabVal": "", "pnl": "0", "pos": "100", "posCcy": "", "posId": "640464230906789953", "posSide": "net", "quoteBal": "", "quoteBorrowed": "", "quoteInterest": "", "realizedPnl": "-0.00019", "sId": 0, "spotInUseAmt": "0", "spotInUseCcy": "BTC", "thetaBS": "33.64693204042858", "thetaPA": "9.504012377647234E-4", "tradeId": "15", "uTime": "1698970571898", "upl": "0.0025819530013177", "uplLastPx": "0.0018", "uplRatio": "0.4694460002395895", "uplRatioLastPx": "0.3272727272727272", "usdPx": "34457.1", "userId": 39471864, "vegaBS": "-6.811811024356156", "vegaPA": "-1.9769707928291187E-4"})]
    risk = Risk(ok.positions)
    # print(risk.spot_shock())
    # risk.extreme_move()
    # print(risk.vega_risk())
    print(risk.extreme_move())