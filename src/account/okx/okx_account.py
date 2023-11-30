from datetime import datetime
from dotenv import load_dotenv
from okx import Account, PublicData
from account.account import BaseAccount
from account.okx.future import Future
from account.okx.option import Option
from datetime import datetime
from pydantic import RootModel
import os
import json

class OKXAccount(BaseAccount):

    def __init__(self) -> None:
        super().__init__()
        cur_date = datetime.now()
        self.market_data_options = []
        self.futures = []
        self.positions = []
        self.m = cur_date.month
        self.d = cur_date.day
        self.market = 'okx'
        self.positions_data_string = f'./data/positions-{self.market}-{self.m}-{self.d}.json'
        self.market_data_string = f'./data/market-{self.market}-{self.m}-{self.d}.json'
        self.futures_data_string = f'./data/futures-{self.market}-{self.m}-{self.d}.json'
        # if there is no json file for today, call API for current positions 
        if not os.path.isfile(self.positions_data_string):
            try:
                load_dotenv()
                okx_api_key = os.getenv('OKX_API_KEY')
                okx_secret_key = os.getenv('OKX_SECRET_KEY')
                okx_passphrase = os.getenv('OKX_PASSPHRASE')
                # Flag either 0 or 1, with 1 being demo trading
                self.publicData = PublicData.PublicAPI(okx_api_key, okx_secret_key, okx_passphrase, False, '0')
                self.account = Account.AccountAPI(okx_api_key, okx_secret_key, okx_passphrase, False, '0')
                # get all required data from api and set it in the current instance
                self.get_market()
                self.get_futures()
                self.get_postions()
            except:
                raise Exception
        else:
            self.read_data_from_json()
    
    def get_market(self):
        try:
            self.vol_dict = {}
            self.mark_price_dict = {}
            _market_data = self.publicData.get_opt_summary(instFamily='BTC-USD')['data']
            self.mark_prices = self.publicData.get_mark_price(instType='OPTION', uly='BTC-USD')['data']
            # set mark prices for each contract
            for inst in self.mark_prices:
                self.mark_price_dict[inst['instId']] = inst['markPx']

            for inst in _market_data:
                self.vol_dict[inst['instId']] = inst['markVol']
                inst['markPx'] = self.mark_price_dict[inst['instId']]
                self.market_data_options.append(Option(**inst))

            self.write_data_to_json(self.market_data_options, self.market_data_string)
            

        except:
            raise Exception    
   
    def get_futures(self):
        _futures_data = self.publicData.get_mark_price(instType='FUTURES', uly='BTC-USD')['data']
        for fut in _futures_data:
            self.futures.append(Future(**fut))
        self.write_data_to_json(self.futures, self.futures_data_string)
     
    def get_postions(self):
        try:
            _positions = self.account.get_positions()['data']
            for p in _positions:
                if p['instId'] in self.vol_dict.keys():
                    p['markVol'] = self.vol_dict[p['instId']]
                    self.positions.append(Option(**p))
            self.write_data_to_json(self.positions, self.positions_data_string)
        except:
            raise Exception
    
    def read_data_from_json(self):
        # set positions
        try:
            # simplified positions
            with open(self.positions_data_string) as position_file, open(self.futures_data_string) as futures_file, open(self.market_data_string) as market_file:
                for p in json.load(position_file):
                    # only looking at BTC options for simplicity
                    if p['instType'] == 'OPTION' and p['ccy'] == 'BTC':
                        self.positions.append(Option(**p))
                
                for f in json.load(futures_file):
                    self.futures.append(Future(**f))

                for o in json.load(market_file):
                    self.market_data_options.append(Option(**o))    
            
        except FileNotFoundError as exp:
            print(exp)
    
    def write_data_to_json(self, objects: [object] = None, file_string: str = ''):
        try:
            _json_string = [RootModel[type(objects[0])](x).model_dump() for x in objects]
            with open(file_string, 'w') as file:                
                json.dump(_json_string, file)
        except FileNotFoundError as exp:
            print(exp)
def main():
    ok = OKXAccount()
    # TODO: serialize lists of objects
    # print(RootModel[Option](ok.positions).model_dump_json())
    # print(ok.futures)
    # print(ok.market_data_options)

if __name__ == '__main__':
    main()