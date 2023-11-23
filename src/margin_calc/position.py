from datetime import datetime

class Position:

    def __init__(self, d) -> None:
        self.ccy = d['ccy']
        self.instId = d['instId']
        self.markPx = float(d['markPx'])
        self.notionalUsd = float(d['notionalUsd'])
        self.optVal = float(d['optVal'])
        self.pos = float(d['pos'])
        self.iv = float(d['iv'])
        self.idxPx = float(d['idxPx'])
        self.delta = float(d['deltaBS'])
        self.gamma = float(d['gammaBS'])
        self.theta = float(d['thetaBS'])
        self.vega = float(d['vegaBS'])
        self.set_options_data()

    def set_options_data(self):
        d = self.instId.split('-')
        # set option type
        self.type = d[-1]
        # set strike price
        self.strike = int(d[3])
        try:
            exp_date = datetime.strptime(d[2], "%y%m%d")
            # dummy date for now
            dummy = datetime.now()
            delta = exp_date-dummy
            self.expiration_days = delta.days
        except ValueError:
            print('Bad date')

    def serialize(self):
        return self.__dict__ 
    

if __name__ == '__main__':
    print('main')