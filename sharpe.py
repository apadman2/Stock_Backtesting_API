import numpy as np
import yfinance as yf
from sklearn.linear_model import LinearRegression


class Sharpe:
    def __init__(self, one, two):
        self.stock = one
        self.start = two

    def sharpe_ratio(self):
        # Get the data for the stock Apple by specifying the stock ticker, start date, and end date
        df = yf.download(self.stock, self.start)
        df = df[['Adj Close']]
        lag1 = df.shift(1)
        zio = df[['Adj Close']] / lag1
        ret = np.log(zio).dropna()
        rp = ret.mean()*252
        sd = ret.std()*np.sqrt(252)
        rf = 0.009
        sh = (rp - rf) / sd
        return float(sh)

    def risk_factor(self):
        df = yf.download(self.stock, self.start)
        df = df[['Adj Close']].resample('M').ffill().pct_change()
        index = yf.download('SPY', self.start)
        index = index[['Adj Close']].resample('M').ffill().pct_change()
        df = df.dropna()
        index = index.dropna()

        Y = df.values.reshape(-1, 1)
        X = index.values.reshape(-1, 1)
        lr = LinearRegression()  # create object for the class
        lr.fit(X, Y)  # perform linear regression
        ab = [str(lr.coef_), str(lr.intercept_)]

        return ab[1][1:-1], ab[0][2:-2]
