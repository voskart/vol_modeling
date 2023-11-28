from dotenv import load_dotenv
from okx import Account, PublicData 
from margin_calc.position import Position
from margin_calc.option import Option
from margin_calc.future import Future
from datetime import datetime, timedelta
import os
import json
import math

class OKXAccount:

    def __init__(self) -> None:
        cur_date = datetime.now()
        self.market_data_options = []
        self.futures = []
        self.positions = []
        self.m = cur_date.month
        self.d = cur_date.day
        file_string = f'./data/positions-{self.m}-{self.d}.json'
        market_data_string = f'./data/market-{self.m}-{self.d}.json'
        futures_data_string = f'./data/futures-{self.m}-{self.d}.json'
        # if there is no json file for today, call API for current positions 
        if not os.path.isfile(file_string):
            try:
                load_dotenv()
                okx_api_key = os.getenv('OKX_API_KEY')
                okx_secret_key = os.getenv('OKX_SECRET_KEY')
                okx_passphrase = os.getenv('OKX_PASSPHRASE')
                # Flag either 0 or 1, with 1 being demo trading
                self.publicData = PublicData.PublicAPI(okx_api_key, okx_secret_key, okx_passphrase, False, '0')
                self.account = Account.AccountAPI(okx_api_key, okx_secret_key, okx_passphrase, False, '0')
                self.set_market_data(market_data_string)
                self.set_positions_api(file_string)
                self.set_futures_data(futures_data_string)
            except:
                raise Exception
        # add logic to check if data was already imported today
        else:
            self.set_market_data_json()
            self.set_account_data_json()
            self.set_positions_json()
            self.set_futures_data_json()
        
    def set_account_data_json(self):
        try:
            f = open('./data/account.json')
            self.account = json.load(f)
            data = self.account['data'][0]
            self.imr = data['imr']
            self.mmr = data['mmr']
            self.equity = data['details'][0]['eq']
            self.notionalUSD = data['notionalUsd']
            self.margin_ratio = data['mgnRatio']
        except FileNotFoundError as exp:
            print(exp)

    def set_futures_data_json(self):
        try:
            with open('./data/futures-{}-{}.json'.format(self.m, self.d)) as f:
                for fut in json.load(f):
                    # maybe create futures class
                    self.futures.append(Future(fut))
        except FileNotFoundError as exp:
            print(exp)

    def set_positions_api(self, file_string):
        try:
            # TODO: think of better way
            self.positions = []
            self.position_data = self.account.get_positions()
            # convert positions to objects
            # set markvol for each contract from vol_dict
            for p in self.position_data['data']:
                if p['instId'] in self.vol_dict.keys():
                    p['markVol'] = self.vol_dict[p['instId']]
                    self.positions.append(Position(p))
            self.write_positions_to_json(file_string)
        except:
            raise Exception

    def set_market_data(self, market_data_string): 
        try:
            self.vol_dict = {}
            self.mark_price_dict = {}
            self.market_data = self.publicData.get_opt_summary(instFamily='BTC-USD')['data']
            self.mark_prices = self.publicData.get_mark_price(instType='OPTION', uly='BTC-USD')['data']
            for inst in self.market_data:
                self.vol_dict[inst['instId']] = inst['markVol']
            self.market_data_options.append(Option(**inst))
            # set mark prices for each contract
            for inst in self.mark_prices:
                self.mark_price_dict[inst['instId']] = inst['markPx']

            self.write_market_data_to_json(market_data_string)
        except:
            raise Exception    
        
    def set_futures_data(self, futures_data_string):
        try:
            # TODO: think of better way
            self.futures_data = self.publicData.get_mark_price(instType='FUTURES', uly='BTC-USD')
            for fut in self.futures_data['data']:
                self.futures.append(Future(fut))
            self.write_futures_data_to_json(futures_data_string)
        except:
            raise Exception
   
    def set_positions_json(self):
        try:
            # simplified positions
            with open('./data/positions-{}-{}.json'.format(self.m, self.d)) as f:
                for p in json.load(f)['data']:
                    # only looking at BTC options for simplicity
                    if p['instType'] == 'OPTION' and p['ccy'] == 'BTC':
                        self.positions.append(Position(p))
        except FileNotFoundError as exp:
            print(exp)
    
    @staticmethod
    def get_options(self, type, tte, delta):
        expiry = self._find_closest_expiry(tte)
        match type:
            case 'c':
                return self._find_contract('c', expiry, delta)
            case 'p':
                return self._find_contract('p', expiry, delta) 
            case _ :
                raise ValueError('Wrong type')

    def _find_closest_expiry(self, tte):
        # expiration in tte
        wanted_expiration = datetime.now() + timedelta(days=tte)
        delta_expiration = math.inf
        closest_expiration = ''
        for inst in self.market_data_options:
            # get expiration from instId
            options_expiration_str = inst.instId.split('-')[2]
            expiration_cur = datetime.strptime(options_expiration_str, '%y%m%d')
            cur_delta = expiration_cur-wanted_expiration
            if abs(cur_delta.days) < delta_expiration:
                delta_expiration = abs(cur_delta.days)
                closest_expiration = options_expiration_str
        return closest_expiration

    # TODO: Create two sets (calls, puts) and order by delta
    def _find_contract(self, type, expiry: str, delta):
        delta_closest = math.inf
        closest_contract = None
        for inst in self.market_data_options:
            # TODO: add call/put field to Option class
            if expiry in inst.instId and inst.instId.split('-')[4].lower() == type:
                if abs(abs(inst.delta)-delta) < delta_closest:
                    closest_contract = inst
                    delta_closest = abs(abs(inst.delta)-delta)
        return closest_contract

    def find_contract_by_strike_exp(self, type, expiry: str, strike: int):
        for inst in self.market_data_options:
                if expiry in inst.instId and inst.instId.split('-')[4].lower() == type and inst.strike == strike:
                    return inst

    def set_market_data_json(self):
        try:
            with open('./data/market-{}-{}.json'.format(self.m, self.d)) as f:
                for inst in json.load(f):
                    self.market_data_options.append(Option(**inst))
        except FileNotFoundError as exp:
            print(exp)

    # TODO: DRY CODE
    def write_positions_to_json(self, file_string):
        if self.position_data:
            try:
                with open(file_string, 'w') as f:
                    json.dump(self.position_data, f)
            except FileNotFoundError as exp:
                print(exp)
        else:
            print('empty')

    def write_market_data_to_json(self, file_string):
        if self.market_data:
            # set mark prices for each contract
            for inst in self.market_data:
                if inst['instId'] in self.mark_price_dict.keys():
                    inst['markPx'] = self.mark_price_dict[inst['instId']]
                self.market_data_options.append(Option(**inst))
            try:
                with open(file_string, 'w') as f:
                    json.dump(self.market_data, f)
            except FileNotFoundError as exp:
                print(exp)
        else:
            print('empty')

    def write_futures_data_to_json(self, file_string):
        if self.futures_data:
            try:
                with open(file_string, 'w') as f:
                    json.dump(self.futures_data['data'], f)
            except FileNotFoundError as exp:
                print(exp)
        else:
            print('empty')

def main():
    ok = OKXAccount()
    # should return both put and call (0.25 delta) with a week expiry
    # print(ok._find_contract('any', 1, 0.25))
    # print(ok._find_closest_expiry(180))

if __name__ == "__main__":
    main()