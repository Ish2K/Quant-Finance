
import redis
from ib_insync import *
import json
import pandas as pd
import pandas_ta as pta
import numpy as np
from pickle import load

# prepare strategy class

class Strategy:
    def __init__(self, ticker, model_path):
        self.ticker = ticker
        self.model = load(open(model_path, 'rb'))

    def get_action(self, state):
        pass

    def processData(self, data):

        data = pd.DataFrame(data)
        # print(df.head())
        data['date'] = pd.to_datetime(data['date'])

        # data['date'] = pd.to_datetime(data['date']).dt.tz_localize("US/Eastern")
        data.set_index('date', inplace=True)

        # data.rename(columns={'open': 'open', 'high': 'high', 'low': 'low', 'close': 'close', 'volume': 'volume'}, inplace=True)

        data["log_return_lag_12"] = np.log(data['close'] / data['close'].shift(12))
        data["log_return_lag_24"] = np.log(data['close'] / data['close'].shift(24))
        data["log_return_lag_36"] = np.log(data['close'] / data['close'].shift(36))

        data["returns_lag_12"] = data['close'].pct_change(12)
        data["returns_lag_24"] = data['close'].pct_change(24)
        data["returns_lag_36"] = data['close'].pct_change(36)

        # data["high_36"] = data['close'].rolling(window=36).max()
        data["low_36"] = data['close'].rolling(window=36).min()

        bb36 = pta.bbands(data['close'], length=36)
        data['bb_lowerband_36'] = bb36['BBL_36_2.0']

        data['rsi'] = pta.rsi(data['close'], length=14)

        data = data[['volume', 'rsi', 'log_return_lag_36', 'returns_lag_36',
       'log_return_lag_24', 'returns_lag_24', 'log_return_lag_12',
       'returns_lag_12', 'bb_lowerband_36', 'low_36']]
        
        return data.dropna()
    
    def run(self):
        
        # create a redis client
        redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0, password="p@ss$12E4")
        # subscribe to the channel
        pubsub = redis_client.pubsub()
        pubsub.subscribe(self.ticker)

        for message in pubsub.listen():
            if message["type"] == "message":
                data = json.loads(message["data"])

                # print(type(data["bars"][0]), len(data["bars"]), data["bars"][0])
                
                data = self.processData(list(data["bars"]))
                print(data.head()   )
                signal = self.model.predict(data)[-1]
                print("Signal: ", signal)
                msg = {"signal": str(signal)}
                redis_client.publish(self.ticker + "_trade", json.dumps(msg))

msft_strategy = Strategy("MSFT", "../models/MSFT_model.pkl")
msft_strategy.run()
