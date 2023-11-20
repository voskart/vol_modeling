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
                    b = black_scholes(idx_price*(1+s/100), pos.strike, r, pos.iv*(1+iv_change/100), pos.expiration_days/365, pos.type.lower())/idx_price*pos.pos/100
                    tmp += b
                min_val = min(tmp, min_val)
        return self.positions_value-abs(min_val)

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
        expiry_dates = np.arange(1,90)
        # linear approximation for above expiries
        iv_values = linear_approximation(initial_iv_change_pct, tte, expiry_dates)
        idx_price = self.positions[0].idxPx
        r = put_call_parity()
        # for each option, calculate the minimum value for a contract while changing tte and iv, then compare to initial contract
        vega_risk = 0
        for pos in self.positions:
            yield
            # calculate deltas for each contract with different expiry dates
            # for each contract, calculate prices for tte 1-90 and corresponding iv change
            # calculate maximum loss for each position simulation
            # calculates max loss by changing expiries and iv shocks
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
        
        min_val = math.inf
        for s in spot_move_pct:
            for pos in self.positions:
                # set mark iv for each contract
                # change in spot price
                b = black_scholes(idx_price*(1+s/100), pos.strike, r, pos.iv, pos.expiration_days/365, pos.type.lower())/idx_price*abs(pos.pos/100)
                min_val = min(b, min_val)
        return (self.positions_value-min_val)/2
    
    def minimum_charge():
        raise NotImplemented
    
if __name__ == '__main__':
    ok = OKXAccount()
    risk = Risk(ok.positions)
    # print(risk.spot_shock())
    print(risk.time_decay())
    # print(risk.extreme_move())