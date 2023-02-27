import time

from TDClient import FData
from creds import *

url = "http://13.126.151.25/"
fdata_object = FData(key='trial', base_url=url)

login = fdata_object.login()
connect = fdata_object.connect_to_server(username=username, password=password, realtime_port=8082,
                                         url='push.truedata.in')

ticksym = fdata_object.add_tick_symbols(['BANKNIFTY-I'])

"""pprint.pprint(login)
pprint.pprint(connect)
pprint.pprint(ticksym)
pprint.pprint(fdata_object.disconnect_from_server())"""


# pprint.pprint(fdata_object.get_tick_data())


# @fdata_object.get_tick_data
def strategy(data_var):
    # print(data_var)
    time.sleep(1)


# Method 1
# @fdata_object.get_tick_data
def strategy(data_var):
    ltp = data_var['BANKNIFTY-I']['ltp']
    profit_amount, loss_amount = '', ''
    if ltp > 100:
        print(f"Bought at {ltp}")
        profit_amount = ltp * 1.1
        loss_amount = ltp * .9
    if profit_amount and loss_amount:
        print(f"Profit at -> {profit_amount}\nLoss at -> {loss_amount}")
    time.sleep(1)


# It will block the code, either use multithreading or use Method 2.
# Method 2
def strategy2(data_var):
    ltp = data_var['BANKNIFTY-I']['ltp']
    profit_amount, loss_amount = '', ''
    if ltp > 100:
        profit_amount = ltp * 1.1
        loss_amount = ltp * .9
    if profit_amount and loss_amount:
        return f"Profit at -> {profit_amount}, Loss at -> {loss_amount}"
    return f"Bought at {ltp}"


# Say you have another function to carry the logic.
def another_function(data_var):
    return f"********{data_var}********"


'''
while True:
    data = fdata_object.get_tick_data()
    result = strategy2(data)
    print(f"Further processing for Result by the strategy 2. -> {result}")
    result2 = another_function(result)
    print(f"Another Function's processing. {result2}")
    time.sleep(1)


'''

"""print(fdata_object.get_historical('BANKNIFTY-I', df=True,duration=1))"""

cursor = 1


def strategy_for_candle(data):
    global cursor
    print(f"{cursor}. Received data -> ", data)
    cursor += 1
    time.sleep(4)


def strt(data):
    data = data['BANKNIFTY-I']
    o = data['Open']
    h = data['High']
    l = data['Low']
    c = data['Close']
    # print(f"open-> {o}, high-> {h}, low-> {l}, close-> {c}")
    print(f"Difference in open and close is: {abs(c - o)}")
    # print(data)


fdata_object.calculate_candles(strategy_function=strategy_for_candle, interval=1, symbol='BANKNIFTY-I', fakeServer=False)
