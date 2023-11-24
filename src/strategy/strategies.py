from margin_calc.okx_account import OKXAccount
from margin_calc.risk import Risk
from margin_calc.model import black_scholes
from margin_calc.helpers import put_call_parity

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
            # print(f"Bull put spread: Long Put: {l_put.instId} with delta: {l_put.delta}, Short Put: {s_put.instId} with delta: {s_put.delta}\n Long Call: {l_call.instId} with delta: {l_call.delta}, Short Call: {s_call.instId} with delta: {s_call.delta}\n for Potential profit of: {s_call.markPx + s_put.markPx}")
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
        return(l_put.markPx, s_put.markPx)

    def compute_yield(self, risk: Risk, tte: int, premium: float) -> float:
        mmr = risk.get_mmr()
        return ((premium/mmr)*(365/tte)*100)
        
 
def main():
    okx = OKXAccount()
    risk = Risk(okx)
    strat = Strategy()
    tte_list = [5, 10, 30, 60]
    iv_shocks = [5, 10, 15]
    spot_shocks = [5, 10, 15]
    
    # for s in spot_shocks:
    #     # simulating spot shock of 5%
    #     for iv in iv_shocks:
    #         _r = Risk(ok, s, iv)
    #         # shock market with both s and i
    #         _r.market_shock(iv)
    #         print('#####')
    #         print(f'Spot shock: {s}, iv shock: {iv}')
    #         print(f'MMR under {_r.idxPrice}: {_r.get_mmr()}')
    #         # premia for expirations
    #         premia = strat.iron_condor_yield(ok, tte_list)
    #         for e, p in zip(tte_list, premia):
    #             y = strat.compute_yield(_r, e, p)
    #             print(f'Yield for expiry {e} days out: {y}% annualized, Index price: {_r.idxPrice}')

    # scenario 1, move ttm by 20 days
    l_put = OKXAccount.find_contract_by_strike_exp(okx, 'p', '231229', 35000)
    s_put = OKXAccount.find_contract_by_strike_exp(okx, 'p', '240126', 35000)

    print(f'Initial prices, long put: {l_put.markPx}, short put: {s_put.markPx}')
    print(risk.get_mmr())

    r = put_call_parity()
    # TODO: implement logic for expiring options
    risk_1 = Risk(okx, 0, 0, -20)
    print(risk_1.get_mmr())
    bs_l_put = black_scholes(risk.idxPrice, l_put.strike, r, l_put.markVol, (l_put.tte-20)/365, l_put.type)/risk.idxPrice
    bs_s_put = black_scholes(risk.idxPrice, s_put.strike, r, s_put.markVol, (s_put.tte-20)/365, s_put.type)/risk.idxPrice
    print(f'Scenario 1, no change, tte decreased by 20 days, long put price: {bs_l_put}, short put price: {bs_s_put}\n')

    # spot goes up by 10%, iv goes up by 10 points
    risk_2 = Risk(okx, 10, 10)
    risk_2.market_shock(10)
    bs_l_put, bs_s_put = strat.diagonal_spread(okx)
    print(f'MMR at price of {risk_2.idxPrice}: {risk_2.get_mmr()}')
    print(f'Scenario 2, spot 10%, iv 10 points, long put price: {bs_l_put}, short put price: {bs_s_put}\n')

    # spot down 10%, iv down 10 points
    risk_3 = Risk(okx, -10, -10)
    risk_3.market_shock(-10)
    bs_l_put, bs_s_put = strat.diagonal_spread(okx)
    print(f'MMR at price of {risk_3.idxPrice}: {risk_3.get_mmr()}')
    print(f'Scenario 3, spot -10%, iv -10 points, long put price: {bs_l_put}, short put price: {bs_s_put}\n')

    # price up 10%, gap closes -> jan iv same, dec iv up
    risk_4 = Risk(okx, -10, 0)
    bs_l_put = black_scholes(risk_4.idxPrice, l_put.strike, r, l_put.markVol, l_put.tte/365, l_put.type)/risk_4.idxPrice
    bs_s_put = black_scholes(risk_4.idxPrice, s_put.strike, r, l_put.markVol, s_put.tte/365, s_put.type)/risk_4.idxPrice
    print(f'MMR at price of {risk_4.idxPrice}: {risk_4.get_mmr()}')
    print(f'Scenario 4, spot -10%, long put price: {bs_l_put}, short put price: {bs_s_put}\n')

if __name__ == '__main__':
    main()    