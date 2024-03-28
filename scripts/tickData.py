from ib_insync import *
import redis
import json
from datetime import datetime, timedelta
import pytz
import pandas as pd

ib = IB()
ib.connect('127.0.0.1', 7497, clientId=3)

today = datetime.now().strftime("%Y%m%d")

reqTickerMapper = {}

redis_client = redis.Redis(host="127.0.0.1", port=6379, db=0, password="p@ss$12E4")

def pendingTickersEvent(tickers):
    for ticker in tickers:
        print("Last: ", ticker.last)

def barUpdateEvent(bars, hasNewBar):
    global reqTickerMapper
    # print(ib.client.getReqId())
    if(hasNewBar and (len(bars) >= 36)):

        ticker = reqTickerMapper[bars.reqId]
        df = util.df(bars)
        df['date'] = pd.to_datetime(df['date']).dt.tz_convert('US/Eastern')

        # convert timestamp to integer

        bars = df.tail(100).to_json(orient='records')

        # convert json to dict
        bars = json.loads(bars)

        # print(bars)

        msg = {"bars": bars}
        redis_client.publish(ticker, json.dumps(msg))
        print("sent!")

tickers = ["MSFT"]

contracts = [Stock(ticker, 'SMART', 'USD') for ticker in tickers]

# ib.pendingTickersEvent += pendingTickersEvent

# ib.reqTickByTickData(contract, 'Last', 0, False)
ib.client._reqIdSeq = 1

for contract in contracts:

    bars = ib.reqHistoricalData(
            contract,
            endDateTime='',
            durationStr='900 S',
            barSizeSetting='5 secs',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1,
            keepUpToDate=True
            )

    reqTickerMapper[bars.reqId] = contract.symbol

ib.barUpdateEvent += barUpdateEvent

# ticker = ib.reqTickByTickData(contract, 'Last', 0, False)

current_time = datetime.now(pytz.timezone('US/Eastern'))

market_close = current_time.replace(hour=16, minute=0, second=0, microsecond=0)

seconds_to_close = (market_close - current_time).total_seconds()

print("Seconds to close: ", seconds_to_close)

ib.sleep(seconds_to_close)

# ib.cancelTickByTickData(ticker)

ib.disconnect()