from dotenv import load_dotenv
from okx import Account, PublicData 
from position import Position
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
            except:
                raise Exception
        # add logic to check if data was already imported today
        else:
            self.set_account_data_json()
            self.set_positions_json()
        
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

    def set_positions_api(self, file_string):
        try:
            self.positions = self.account.get_positions()
            # set markvol for each contract from vol_dict
            for p in self.positions['data']:
                if p['instId'] in self.vol_dict.keys():
                    p['iv'] = self.vol_dict[p['instId']]
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

    def write_positions_to_json(self, file_string):
        if self.positions:
            try:
                with open(file_string, 'w') as f:
                    json.dump(self.positions, f)
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

    def calculate_mmr(self):
        raise NotImplemented         
    
            

def main():
    ok = OKXAccount()

if __name__ == "__main__":
    main()