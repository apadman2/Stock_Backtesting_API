import yfinance as yf
import pandas as pd
import itertools

class KVO:
    def __init__(self, one, two, three):
        self.ticker = one
        self.start = two
        self.today = three

    def kvo(self):
        # Get the data for the stock Apple by specifying the stock ticker, start date, and end date
        df = yf.download(self.ticker, self.start, self.today)
        df = pd.DataFrame(df)
        df['ema_slow'] = df['Adj Close'].ewm(span=20, min_periods=0,  adjust=False, ignore_na=False).mean()
        df['ema_fast'] = df['Adj Close'].ewm(span=10, min_periods=0,  adjust=False, ignore_na=False).mean()
        df['ema_diff'] = df['ema_fast'] - df['ema_slow']
        df['signal'] = df['ema_diff'].ewm(span=10, min_periods=0,  adjust=False, ignore_na=False).mean()
        pos = 0
        num = 0
        d = 0
        percentchange = []
        date = []
        for i in df.index:
            diff = df['ema_diff'][i]
            sig = df['signal'][i]
            close = df['Adj Close'][i]
            if diff > sig:
                if pos == 0:
                    bp = close
                    pos = 1
                    # BUY
            elif diff < sig:
                # BWR
                if pos == 1:
                    pos = 0
                    sp = close
                    # SELL
                    pc = (sp / bp - 1) * 100
                    percentchange.append(float(pc))
                    date.append(i)

            if num == df["Adj Close"].count() - 1 and pos == 1:
                pos = 0
                sp = close
                # SELL
                pc = (sp / bp - 1) * 100
                percentchange.append(float(pc))
                date.append(i)

            num += 1

        gains = 0
        ng = 0
        losses = 0
        nl = 0
        total_return = 1
        d += 1

        for i in percentchange:
            if i > 0:
                gains += i
                ng += 1
            else:
                losses += i
                nl += 1
            total_return = total_return * ((i / 100) + 1)

        total_return = round((total_return - 1) * 100, 2)

        if ng > 0:
            avg_gain = round((gains / ng), 2)
            max_return = (round(max(percentchange), 2))
        else:
            avg_gain = 0
            max_return = "undefined"

        if nl > 0:
            avg_loss = round((losses / nl), 2)
            max_loss = (round(min(percentchange), 2))
            ratio = (round((-avg_gain / avg_loss), 2))
        else:
            avg_loss = 0
            max_loss = "undefined"
            ratio = "inf"

        # Results
        x = [ng + nl, ratio, avg_gain, avg_loss, max_return, max_loss,
             total_return]

        returns = list(itertools.repeat(float(1), len(df.index)))
        for i in range(len(df.index)):
            for j in range(len(date)):
                if df.index[i] == date[j]:
                    returns[i] = (percentchange[j]/100)+1
        for i in range(len(df.index)):
            if i == df.index[0]:
                returns[0] = 1
            else:
                temp = returns[i-1]
                returns[i] = temp * returns[i]

        return x, returns

