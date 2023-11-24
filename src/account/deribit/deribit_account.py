from account import Account

class DeribitAccount(Account):
    
    def __init__(self) -> None:
        super().__init__()

    def get_postions(self):
        return super().get_postions()

    def get_futures(self):
        return super().get_futures()
    
    def read_data_from_json(self):
        return super().read_data_from_json()
    
    def write_data_to_json(self):
        return super().write_data_to_json()