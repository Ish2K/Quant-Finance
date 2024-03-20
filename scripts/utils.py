def loadDataIBKR(ib, symbol, endDateTime, durationStr, barSizeSetting, whatToShow, useRTH, formatDate, keepUpToDate):

    contract = Stock(symbol, 'SMART', 'USD')
    bars = ib.reqHistoricalData(
            contract,
            endDateTime='20240315 09:15:00 US/Eastern',
            durationStr='900 S',
            barSizeSetting='5 secs',
            whatToShow='TRADES',
            useRTH=True,
            formatDate=1,
            keepUpToDate=True
            )
    return bars

