import numpy as np
import math
from scipy.stats import norm
import inspect

'''
:param S: spot price
:param K: strike price
:param r: risk-free interest rate
:param sigma: volatility of the asset
:param T: time to maturity
:param type: either call (c) or put (p)

'''
def black_scholes(S, K, r, sigma, T, type):
    # print(sigma*np.sqrt(T), T, np.sqrt(T), S, K, type)
    d1 = (np.log(S/K)+(r+sigma**2/2.)*math.ceil(T))/(sigma*np.sqrt(math.ceil(T)))
    d2 = d1 - sigma*(np.sqrt(T))
    if type == 'c':
        return S*norm.cdf(d1) - norm.cdf(d2)*K*np.exp(-r*T)
    elif type == 'p':
        return norm.cdf(-d2)*K*np.exp(-r*T) - norm.cdf(-d1)*S
    else:
        raise ValueError('Wrong type passed!')

def main():
    spot_price = 35669
    # price of a btc call option expiring in 10 days
    btc_exp_10 = black_scholes(35600, 35500, 0, 0.56, 1/365, 'c')
    # price of a btc call option expiring in 30 days
    btc_exp_30 = black_scholes(35600, 33000, 0, 0.56, 3/365, 'c')
    print(btc_exp_10/spot_price, btc_exp_30/spot_price)


if __name__ == "__main__":
    main()
