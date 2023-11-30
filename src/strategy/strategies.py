from margin_calc.risk import Risk
from margin_calc.scenario import Scenario
from margin_calc.model import black_scholes
from account.okx.okx_account import OKXAccount
from account.util import put_call_parity

import numpy as np
import math

class Strategy:
    def __init__(self) -> None:
        pass

    '''
    Looking to sell iron condors, selling at 30 delta, buying at 10 delta
    Essentially bull put spread and bear call spread
    '''
    def iron_condor_yield(self, okx: OKXAccount, tte: [int]) -> float:
        yields = []
        for e in tte:
            # get 10 delta contracts
            l_call = OKXAccount.get_options(okx, 'c', e, 0.1)
            l_put = OKXAccount.get_options(okx, 'p', e, 0.1)

            # get 30 delta contracts
            s_call = OKXAccount.get_options(okx, 'c', e, 0.3)
            s_put = OKXAccount.get_options(okx, 'p', e, 0.3)
            
            # maximum profit if btc between strikes of short options
            print(f"Bull put spread: Long Put: {l_put.instId} with delta: {l_put.delta}, Short Put: {s_put.instId} with delta: {s_put.delta}\n Long Call: {l_call.instId} with delta: {l_call.delta}, Short Call: {s_call.instId} with delta: {s_call.delta}\n for Potential profit of: {s_call.markPx + s_put.markPx}")
            yields.append(s_call.markPx + s_put.markPx)
        return yields

    '''
    Simulating calendar spread, betting on the gap between 35k dec and january puts
    '''
    def diagonal_spread(self, risk: Risk) -> float:
        # long put 
        l_put = OKXAccount.find_contract_by_strike_exp(risk, 'p', '231229', 35000)
        # short put
        s_put = OKXAccount.find_contract_by_strike_exp(risk, 'p', '240126', 35000)
        return(l_put, s_put)

    def compute_yield(self, risk: Risk, tte: int, premium: float) -> float:
        mmr = risk.get_mmr()
        return ((premium/mmr)*(365/tte)*100)
        
def main():
    okx = OKXAccount()
    risk = Risk(okx)
    strat = Strategy()
    r = put_call_parity(acc=risk.account, spot=risk.idxPrice)
    # iv shock, spot shock, tte shift
    # print(strat.diagonal_spread(okx))
    # print(f'Initial MMR: {risk.get_mmr()}') 
    # # add diagonal spread contracts
    # risk.positions = []
    # risk.add_positions(strat.diagonal_spread(okx))
    # risk.calculate_portfolio_value()
    # print(risk.positions_value)
    # print(f'MMR after diagonal spread contracts: {risk.get_mmr()}')
    # scenario = Scenario(10, 10, 0, risk)    
    # # we need to add the respective contracts to the portfolio
    # print(f'MMR under 10% iv and spot shock: {scenario.get_mmr()}')
    futures = okx.futures
    avg = 0
    for pos in risk.positions:
        new_price = black_scholes(pos.idxPx, pos.strike, 0.12, pos.markVol, pos.tte/365, pos.type.lower())/pos.idxPx
        print(f'contract: {pos.instId}, mark vol: {pos.markVol}, idx px: {pos.idxPx}, okx mark price: {pos.markPx}, bs model price: {new_price}, diff: {(pos.markPx-new_price)/pos.markPx*100:,.2f} %'.format())
        avg += (pos.markPx-new_price)/pos.markPx
    avg = avg/len(risk.positions)
    print(f'avg error with rfr of {0.12}: {avg:.2f}')
    
if __name__ == '__main__':
    main()    