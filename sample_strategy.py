import pprint
import time

from TDClient import FData
from creds import *

nurl = "http://13.126.151.25/"
url = "http://13.232.116.35/"

fdata_object = FData(key='trial', base_url=url)
login = fdata_object.login()
fdata_object.disconnect_from_server()
connect = fdata_object.connect_to_server(username=username, password=password, realtime_port=8082,
                                         url='push.truedata.in')
ticksym = fdata_object.add_tick_symbols(
    ['BANKNIFTY-I', 'BHARTIARTL', 'TCS', 'RELIANCE', 'HDFC', 'HDFCBANK', 'KOTAKBANK', 'HINDALCO',
     'TATAMOTORS', 'TATASTEEL', 'TATAPOWER', 'TATACONSUM', 'TATACHEM', 'TATAELXSI'])

"""fdata_object.headers['key'] = 'AdMiN@#wWeAlThWiSeRs'
fdata_object.disconnect_from_server()"""
# connect = fdata_object.connect_to_server(username=username, password=password, realtime_port=8082,
#                                         url='push.truedata.in')
# ticksym = fdata_object.add_tick_symbols(['BANKNIFTY-I', 'BHARTIARTL'])
"""fdata_object.add_option_symbols('BANKNIFTY', 2023, 3, 30)
fdata_object.add_option_symbols('TCS', 2023, 3, 30)
fdata_object.add_option_symbols('RELIANCE', 2023, 3, 30)
fdata_object.add_option_symbols('HDFC', 2023, 3, 30)
fdata_object.add_option_symbols('HDFCBANK', 2023, 3, 30)"""

"""pprint.pprint(login)
pprint.pprint(connect)
pprint.pprint(ticksym)
pprint.pprint(fdata_object.disconnect_from_server())"""

# pprint.pprint(fdata_object.get_tick_data())


"""@fdata_object.get_oc_data
def strategy(data_var):
    # print(pandas.DataFrame.from_dict(data_var['BANKNIFTY202332']).to_csv('oc.csv'))
    print(data_var.keys())
    time.sleep(10)
    print(data_var)"""


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


"""
while True:
    data = fdata_object.get_tick_data()
    print(data)
    
    result = strategy2(data)
    print(f"Further processing for Result by the strategy 2. -> {result}")
    result2 = another_function(result)
    print(f"Another Function's processing. {result2}")
    time.sleep(1)"""

# print(fdata_object.get_historical('BANKNIFTY-I', df=True))

cursor = 1


def strategy_for_candle(data):
    global cursor
    print(f"{cursor}. Received data -> ", data["BANKNIFTY-I"])
    if data['BANKNIFTY-I']['ltp'] > 500:
        print("SL has been hit, Please exit the trade.")
    cursor += 1
    time.sleep(1)


def strt(data):
    data = data['BANKNIFTY-I']
    o = data['Open']
    h = data['High']
    l = data['Low']
    c = data['Close']
    # print(f"open-> {o}, high-> {h}, low-> {l}, close-> {c}")
    print(f"Difference in open and close is: {abs(c - o)}")
    # print(data)


# fdata_object.calculate_candles(strategy_function=strategy_for_candle, interval=3)
'''print(fdata_object.get_historical('BHARTIARTL', df=True))
'''

'''def abc():
    print(time.perf_counter())
    for sym in fdata_object.all_symbols:
        print(pandas.DataFrame.from_dict(fdata_object.get_last_candles(sym, interval=3, size=1)))
    print(time.perf_counter())


thread = threading.Thread(target=abc)
thread.start()
'''

'''for x in range(50):
    print(f"LTP -> {x}")
    time.sleep(.1)
'''

'''t = 1
m = None
while True:
    if t == 1 and (m == None or m % 3 == 0):
        dd = fdata_object.candle(interval=3)
        """print("************BANKNIFTY-I***************")
        print(dd['BANKNIFTY-I'])
        print("************BHARTIARTL***************")
        print(dd['BHARTIARTL'])"""
        print(f"Last candle BANKNIFTY-I @ -> {dd['BANKNIFTY-I'].iloc[-1].to_dict()}")
        print(f"Last candle BHARTIARTL @ -> {dd['BHARTIARTL'].iloc[-1].to_dict()}")
    tt = datetime.now().time()
    t = tt.second
    m = tt.minute
'''

pprint.pprint(fdata_object.get_last_candles(interval=3, size=3))
#pprint.pprint(fdata_object.candle(interval=3))
