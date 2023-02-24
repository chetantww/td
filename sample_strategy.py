import time

from TDClient import FData
from creds import *

url = "http://13.126.151.25/"
wwd = FData(key='trial', base_url=url)

login = wwd.login()
connect = wwd.connect_to_server(username=username, password=password, realtime_port=8082, url='push.truedata.in')
ticksym = wwd.add_tick_symbols(['BANKNIFTY-I'])

"""pprint.pprint(login)
pprint.pprint(connect)
pprint.pprint(ticksym)
pprint.pprint(wwd.disconnect_from_server())"""


# pprint.pprint(wwd.get_tick_data())


# @wwd.get_tick_data
def strategy(data_var):
    # print(data_var)
    time.sleep(1)


"""s = 'BHARTIARTL-I'
pandas.DataFrame.from_records(wwd.get_historical(s)).to_csv(f"{s}_20230222.csv")"""


# Method 1
# @wwd.get_tick_data
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






# print(wwd.get_historical('BANKNIFTY-I', df=True,duration=5))

wwd.calculate_candles(1)
starting_point = len(wwd.candles)
while True:
    if len(wwd.candles) > starting_point:
        print("wwd.candles -> ", wwd.candles)
        wwd.candles = {}
        starting_point += 1
