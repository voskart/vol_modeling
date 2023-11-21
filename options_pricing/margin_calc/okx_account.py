from dotenv import load_dotenv
from okx import Account, PublicData 
from position import Position
from future import Future
from datetime import datetime
import os
import json

class OKXAccount:

    def __init__(self) -> None:
        cur_date = datetime.now()
        m = cur_date.month
        d = cur_date.day
        file_string = f'./data/positions-{m}-{d}.json'
        market_data_string = f'./data/market-{m}-{d}.json'
        futures_data_string = f'./data/futures-{m}-{d}.json'
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
        cur_date = datetime.now()
        m = cur_date.month
        d = cur_date.day
        self.futures = []
        try:
            with open('./data/futures-{}-{}.json'.format(m, d)) as f:
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
                    p['iv'] = self.vol_dict[p['instId']]
                    self.positions.append(Position(p))
            self.write_positions_to_json(file_string)
        except:
            raise Exception

    def set_market_data(self, market_data_string): 
        try:
            self.vol_dict = {}
            self.market_data = self.publicData.get_opt_summary(instFamily='BTC-USD')['data']
            for inst in self.market_data:
                self.vol_dict[inst['instId']] = inst['markVol']
            self.write_market_data_to_json(market_data_string)
        except:
            raise Exception    
        
    def set_futures_data(self, futures_data_string):
        try:
            # TODO: think of better way
            self.futures = []
            self.futures_data = self.publicData.get_mark_price(instType='FUTURES', uly='BTC-USD')
            for fut in self.futures_data['data']:
                self.futures.append(Future(fut))
            self.write_futures_data_to_json(futures_data_string)
        except:
            raise Exception

    def set_positions_json(self):
        self.positions = []
        cur_date = datetime.now()
        m = cur_date.month
        d = cur_date.day
        try:
            # simplified positions
            with open('./data/positions-{}-{}.json'.format(m, d)) as f:
                for p in json.load(f)['data']:
                    # only looking at BTC options for simplicity
                    if p['instType'] == 'OPTION' and p['ccy'] == 'BTC':
                        self.positions.append(Position(p))
        except FileNotFoundError as exp:
            print(exp)

    def set_market_data_json(self):
        raise NotImplemented
    

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


    def calculate_mmr(self):
        raise NotImplemented         
    
            

def main():
    ok = OKXAccount()

if __name__ == "__main__":
    main()