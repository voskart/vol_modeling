from position import Position
from okx_account import OKXAccount
from model import black_scholes
from helpers import put_call_parity, linear_approximation, get_calls
import math
import numpy as np

class Risk(OKXAccount):

    def __init__(self) -> None:
        OKXAccount.__init__(self)
        self.positions = self.positions
        self.positions_value = self.calculate_portfolio_value()
        self.idxPrice = self.positions[0].idxPx

    def calculate_portfolio_value(self):
        cur_val = 0
        for pos in self.positions:
            cur_val += pos.optVal
        return cur_val

    '''
    Calculates spot shock scenarios based on OKX documentation at 0, 5, 10 and 15% and 0, 30 and 60 days to exp
    '''
    def spot_shock(self) -> float:
        spot_move_pct = [0, -5, 5, -10, 10, -15, 15]
        # point change in IV, 30 would result in a change from 50% to 80% (0, 30 and 60 days respectively)
        # iv_change_pct = [50, 35, 25]
        iv_change_points = [30, 25, 20]
        min_val = math.inf
        r = put_call_parity()
        # for all combinations, calculate new option prices and corresponding portfolio value
        for s in spot_move_pct:
            for _vol_change in iv_change_points:
                # iterate through portfolio and update pricing
                # setting spot price, and iv
                # set mark iv for each contract
                tmp = 0
                for pos in self.positions:
                    # change in spot price as well as change in IV
                    b = (black_scholes(self.idxPrice*(1+s/100), pos.strike, r, pos.iv*(1+_vol_change/100), pos.expiration_days/365, pos.type.lower())/self.idxPrice)*pos.pos/100
                    tmp += b
                min_val = min(min_val, tmp)
        return abs(self.positions_value-min_val)

    '''
    Calculates the theta decay for a 24h period
    '''
    def time_decay(self) -> float:
        theta_decay = 0
        for pos in self.positions:
            theta_decay += pos.theta
        return theta_decay/self.idxPrice
    
    # tbd what "It measures the risk of change in implied volatility across different expiry dates that is not captured in MR1." means exactly
    def vega_risk(self):
        # initial iv change percent for 0, 30 and 60 days
        tte = [0, 30, 60]
        initial_iv_change_pct = [50, 35, 25]
        # expiry_dates = np.arange(1,90)
        expiry_dates = [15, 45, 75]
        # linear approximation for above expiries
        iv_values = linear_approximation(initial_iv_change_pct, tte, expiry_dates)
        r = put_call_parity()
        vega_risk = []
        # need to get several contracts with their mark_vol and simulate iv shock
        btc_instruments = get_calls()
        for inst in btc_instruments:
            init_px = black_scholes(self.idxPrice, float(inst['strike']), r, float(inst['markVol']), inst['expiration_days']/365, 'c')
            tmp = 0
            for iv in iv_values:
                b = black_scholes(self.idxPrice, float(inst['strike']), r, float(inst['markVol'])*(1+iv/100), inst['expiration_days']/365, 'c')
                tmp += abs(init_px - b)
            vega_risk.append(tmp/self.idxPrice)
        return sum(vega_risk)/len(vega_risk)


    '''
    Calculates the risk that arises from differences in contract prices for the same underlying with different expiries
    '''
    def basis_risk(self):
        # maximum forward basis move
        max_fwd_basis_move = 30
        # maximum forward price move
        max_price_fwd_move = 0.015
        # calculate risk for each futures contract
        basis_risk = 0
        for fut in self.futures:
            fwd_basis_move = (self.idxPrice - fut.markPx) * max_fwd_basis_move/100
            fwd_price_move = fut.markPx * max_price_fwd_move
            basis_risk += fwd_basis_move + fwd_price_move
        return basis_risk/self.idxPrice

    
    '''
    Calculates the risk in the case of changes in interest rates by populating a PCA rate movement table
    TODO: model full-on yield curve 
    '''
    def interest_rate_risk(self):
        # parallel shift
        pc1 = [3, 2, 1.75, 1.5, 1, 0.9, 0.8, 0.7]
        # slope change
        pc2 = [4, 3, 2, 1, 0, -0.5, -0.75, -0.9]
        pc1_pct = [5, -5, 2.5, -2.5, 2, -2]
        pc2_pct = [3, -3]
        # need to get yield for 1 day to 720 days out and then shift the curve accordingly
        return 0

    '''
    Calculates the risk in case the underlying experiences a large move. Contrary to spot_shock, IV remains unchanged
    MR of a risk unit is half of the maximum loss when BTC-USD moves +30% or -30%, whichever is larger
    '''
    def extreme_move(self) -> float:
        spot_move_pct = [-30, 30]
        r = put_call_parity()
        min_val = math.inf
        for s in spot_move_pct:
            tmp = 0
            for pos in self.positions:
                # set mark iv for each contract
                # change in spot price
                b = (black_scholes(self.idxPrice*(1+s/100), pos.strike, r, pos.iv, pos.expiration_days/365, pos.type.lower())/self.idxPrice)*pos.pos/100
                tmp += b
            min_val = min(min_val, tmp)
        return abs(self.positions_value-min_val)/2
    
    '''
    Calculates the minimum charge to close options
    '''
    def minimum_charge(self):
        # slippage long options: = min{max(min_per_delta, min_per_delta *abs(delta)), Mark Price} * contract_multiplier
        # slippage short options: max(min_per_delta, min_per_delta * abs(delta)) * contract_multiplier
        # cost per contract: min (taker fee * contract value * contract multiplier, 12.5% * mark price * contract value * contract multiplier)
        min_per_delta = 0.02
        taker_fee = 0.003
        minimum_charge = 0
        for pos in self.positions:
            cost = 0
            if pos.pos < 0:
                slippage = max(min_per_delta, min_per_delta*pos.delta)*abs(pos.pos)
                cost = min(taker_fee * pos.markPx/100 * slippage * abs(pos.pos), 0.125 * pos.markPx * slippage * pos.markPx/100 * abs(pos.pos))
            else:
                slippage = min(max(min_per_delta, min_per_delta*pos.delta), pos.markPx)*abs(pos.pos)
                cost = min(taker_fee * pos.markPx/100 * slippage * abs(pos.pos), 0.125 * pos.markPx * slippage * pos.markPx/100 * abs(pos.pos))
            minimum_charge += cost
        return minimum_charge
    
if __name__ == '__main__':
    ok = OKXAccount()
    risk = Risk()
    print(len(risk.positions))
    print(risk.positions_value)
    print(f'MR1: Spot shock: {risk.spot_shock()}')
    print(f'MR2: Time decay: {risk.time_decay()}')
    print(f'MR3: Vega risk: {risk.vega_risk()}')
    print(f'MR4: Basis risk: {risk.basis_risk()}')
    print(f'MR6: Extreme move: {risk.extreme_move()}')
    print(f'MR7: Minimum charge: {risk.minimum_charge()}')
    max_risk = max(max(risk.spot_shock(), risk.time_decay(), risk.extreme_move())+risk.basis_risk()+risk.vega_risk()+risk.interest_rate_risk(), risk.minimum_charge())
    print(max_risk)