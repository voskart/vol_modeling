from margin_calc.okx_account import OKXAccount
from margin_calc.risk import Risk

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


    def compute_yield(self, risk: Risk, tte: int, premium: float) -> float:
        mmr = risk.get_mmr()
        return ((premium/mmr)*(365/tte)*100)
        
 
def main():
    ok = OKXAccount()
    risk = Risk(ok)
    strat = Strategy()
    tte = [5, 10, 30, 60]
    premia = strat.iron_condor_yield(ok, tte)
    for e, p in zip(tte, premia):
        y = strat.compute_yield(risk, e, p)
        print(f'Yield for expiry {e} days out: {y}% annualized')
    

if __name__ == '__main__':
    main()    