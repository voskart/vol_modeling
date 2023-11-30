from account.okx.okx_account import OKXAccount
from account.util import put_call_parity
from margin_calc.model import black_scholes
from margin_calc.risk import Risk
from copy import deepcopy

class Scenario():

    def __init__(self, iv_shock: int = 0, spot_shock: int = 0, tte_shift: int = 0, risk: Risk = None) -> None:
        self.iv_shock = iv_shock
        self.spot_shock = spot_shock
        # a shift of 20 would mean 20 days would be subtracted from the expiration dates
        self.tte_shift = tte_shift
        self.risk = deepcopy(risk)
        self.r = put_call_parity(risk.account)
        self.idxPx = risk.positions[0].idxPx if risk.positions else 0
        self._market_shock()
        self._adjust_expiries()

    # def add_positions(self, positions: [Position] = None) -> None:
    #     for pos in positions:
    #         self.risk.positions.append(pos)

    '''
    Simulates a shift in expiries while maintaining iv and spot price 
    '''
    def _adjust_expiries(self) -> None:
        # go through positions and check for expiration
        if self.tte_shift:
            for pos in self.risk.positions:
                if pos.tte > self.tte_shift:
                    new_price = black_scholes(self.idxPx, pos.strike, self.r, pos.markVol, (pos.tte-self.tte_shift)/365, pos.type.lower())/self.idxPx
                    pos.optVal = new_price * pos.pos/100
                else:
                    self.risk.positions.remove(pos)
            self.risk.positions_value = self.risk.calculate_portfolio_value()

    '''
    Simulates market conditions based on iv and spot shock and recalculates portfolio value including mmr
    '''
    def _market_shock(self) -> float:
        # update the positions
        for pos in self.risk.positions:
            new_price = black_scholes(self.idxPx*(1+self.spot_shock/100), pos.strike, self.r, pos.markVol+self.iv_shock/100, pos.tte/365, pos.type.lower())/(self.idxPx*(1+self.spot_shock/100))
            pos.optVal = new_price * pos.pos/100
        # update the market
        for pos in self.risk.account.market_data_options:
            new_price = black_scholes(self.idxPx*(1+self.spot_shock/100), pos.strike, self.r, pos.markVol+self.iv_shock/100, pos.tte/365, pos.type)/self.idxPx*(1+self.spot_shock/100)
            pos.markPx = new_price
        self.risk.positions_value = self.risk.calculate_portfolio_value()
    
    def get_mmr(self) -> float:
        return self.risk.get_mmr()

def main():
    ok = OKXAccount()
    risk = Risk(ok)
    print(f'Initial MMR: {risk.get_mmr()}')
    sc1 = Scenario(0, 30, 0, risk)
    sc2 = Scenario(0, 0, 0, risk)
    sc3 = Scenario(0, 0, 20, risk)
    print(f'MMR under spot shock +30%: {sc1.get_mmr()}, portoflio positons: {len(sc1.risk.account.positions)}')
    print(f'MMR under spot shock of 0%: {sc2.get_mmr()}, portoflio positons: {len(sc2.risk.account.positions)}')
    print(f'MMR under -20 tte shift: {sc3.get_mmr()}, portoflio positons: {len(sc3.risk.account.positions)}')

if __name__ == '__main__':
    main()