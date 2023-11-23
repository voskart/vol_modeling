from account import Account

class OKXAccount(Account):

    def __init__(self) -> None:
        super().__init__()

    def get_futures(self):
        return super().get_futures()
     
    def get_postions(self):
        return super().get_postions()
    
    def read_data_from_json(self):
        return super().read_data_from_json()
    
    def write_data_to_json(self):
        return super().write_data_to_json()

def main():
    ok = OKXAccount()

if __name__ == '__main__':
    main()