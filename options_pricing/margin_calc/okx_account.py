from dotenv import load_dotenv
from okx import Account
from position import Position
import os
import json

class OKXAccount:

    def __init__(self, api=False) -> None:
        if api:
            try:
                load_dotenv()
                okx_api_key = os.getenv('OKX_API_KEY')
                okx_secret_key = os.getenv('OKX_SECRET_KEY')
                okx_passphrase = os.getenv('OKX_PASSPHRASE')
                # Flag either 0 or 1, with 1 being demo trading
                self.account = Account.AccountAPI(okx_api_key, okx_secret_key, okx_passphrase, False, '0')
                self.positions = self.get_positions_api()
            except:
                raise Exception
        else:
            self.set_account_data_json()
            self.set_positions_json()
        
    def get_positions_api(self):
        try:
            return(self.account.get_positions())
        except:
            raise Exception
        
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
    
    def set_positions_json(self):
        self.positions = []
        try:
            # simplified positions
            with open('./data/positions_test.json') as f:
                for p in json.load(f)['data']:
                    self.positions.append(Position(p))
        except FileNotFoundError as exp:
            print(exp)

    def calculate_mmr(self):
        raise NotImplemented         
    
            

def main():
    ok = OKXAccount()
    
if __name__ == "__main__":
    main()