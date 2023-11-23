from margin_calc.okx_account import OKXAccount
from margin_calc.risk import Risk

class Stategy:
    def __init__(self) -> None:
        pass

    '''
    Looking to sell iron condors, selling at 30 delta, buying at 10 delta
    '''
    def iron_condor_yield(self) -> None:
        raise NotImplemented
    
def main():
    yield

if __name__ == '__main__':
    ok = OKXAccount()
    print(ok.get_options('c', 30, 0.25))