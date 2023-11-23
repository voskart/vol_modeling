from datetime import datetime

class Future:

    def __init__(self, d) -> None:
        self.markPx = float(d['markPx'])
        self.instId = d['instId']
        self._set_expiry()
    
    def _set_expiry(self) -> None:
        d = self.instId.split('-')
        try:
            exp_date = datetime.strptime(d[2], "%y%m%d")
            # dummy date for now
            dummy = datetime.now()
            delta = exp_date-dummy
            self.expiration_days = delta.days
        except ValueError:
            print('Bad date')



