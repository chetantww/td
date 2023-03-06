import random
import threading
import time
from datetime import datetime, timedelta

import pandas
import requests


def make_candle(df, interval, dtype):
    timestamp_format = '%Y-%m-%d %H:%M:%S'
    assert isinstance(interval, int), "Interval must be an integer"
    d = {'o': 'first', 'h': 'max', 'l': 'min', 'c': 'last', 'v': 'sum'}
    df['time'] = pandas.to_datetime(df['time'], format='%a, %d %b %Y %H:%M:%S %Z')
    df['time'] = df['time'].dt.strftime(timestamp_format)
    df['time'] = pandas.to_datetime(df['time'], format=timestamp_format)
    df.sort_values('time', inplace=True)
    ddf = df.resample(f'{interval}T', on='time').agg(d)
    if dtype == 'dict':
        return ddf.to_dict()
    if dtype == 'df':
        return ddf


def abcd(NN, df):
    z = NN.second
    NN = NN.replace(second=0)
    for x, y in df[df.index == NN].iterrows():
        if z == 0:
            cr = y['o']
        elif z == 59:
            cr = y['c']
        elif z == 10:
            cr = y['l']
        elif z == 50:
            cr = y['h']
        else:
            cr = random.uniform(y['l'], y['h'])
        return round(cr, 2)


class FData:
    tick_data = None
    headers = {'key': 'trial', 'token': None}
    all_symbols = set()
    base_url = 'http://127.0.0.1:5000'
    candles = {}

    def __init__(self, key, base_url=None, debug=False):
        self.headers['key'] = key
        if base_url is not None:
            FData.base_url = base_url
            self.base_url = base_url
        if debug is True:
            self.headers['debug'] = 'true'

    def login(self):
        response = requests.post(self.base_url + '/login', headers=self.headers)
        if 'token' in response.json():
            self.headers['token'] = response.json()['token']
        return response

    def connect_to_server(self, username, password, realtime_port, url):
        data = {'username': username, 'password': password, 'port': realtime_port, 'url': url}
        response = requests.post(self.base_url + '/connect', headers=self.headers, json=data)
        return response

    def disconnect_from_server(self):
        # self.headers['key'] =
        response = requests.post(self.base_url + '/disconnectt', headers=self.headers)

    def add_tick_symbols(self, symbols):
        if isinstance(symbols, list):
            [self.all_symbols.add(x) for x in symbols]
            response = requests.post(self.base_url + '/ticksymbols', headers=self.headers,
                                     json={'Symbols': list(self.all_symbols)})
            return response
        elif isinstance(symbols, str):
            self.all_symbols.add(symbols)
            response = requests.post(self.base_url + '/ticksymbols', headers=self.headers,
                                     json={'Symbols': list(self.all_symbols)})
            return response
        else:
            print("Invalid format to add symbols.")

    def add_option_symbols(self, symbol=None, expiry_year=None, expiry_month=None, expiry_day=None):
        assert symbol is not None and expiry_year is not None and expiry_month is not None and expiry_day is not None, "Invalid input for Option chain."
        js = {'Symbols': [{'symbol': symbol, 'expiry_year': expiry_year,
                           'expiry_month': expiry_month, 'expiry_day': expiry_day}]}
        response = requests.post(FData.base_url + '/ocsymbols', headers=self.headers,
                                 json=js)
        return response

    @staticmethod
    def get_oc_data(passed_func=None):
        while True:
            data = requests.get(FData.base_url + '/getocdata', headers=FData.headers)
            option_chain = data.json()
            if passed_func == None:
                return option_chain
            passed_func(option_chain)

    @staticmethod
    def get_tick_data(passed_func=None):
        while True:
            try:
                data = requests.get(FData.base_url + '/gettickdata', headers=FData.headers)
                tick_data = data.json()
                filtered_data = {sym_dict['symbol']: sym_dict for sym_dict in tick_data if
                                 sym_dict['symbol'] in FData.all_symbols}
                if passed_func == None:
                    return filtered_data
                passed_func(filtered_data)
            except requests.exceptions.JSONDecodeError as e:
                print("Json Error Occurred")
            except TypeError:
                print(f"Type error occurred, this is the Tickdata-> {tick_data}")
                raise Exception

    @staticmethod
    def get_historical(sym, start=None, end=None, duration=None, df=False):
        if not isinstance(duration, int):
            duration = None
        '''start, end = None, None'''
        jsn = {'Duration': duration, 'End': end, 'Start': start}
        if isinstance(sym, str):
            sym = [sym]
        if isinstance(sym, list):
            response = {}
            for s in sym:
                jsn['Symbol'] = s
                resp = requests.get(FData.base_url + '/histdata', headers=FData.headers,
                                    json=jsn)
                response[s] = resp.json()
            if df is True:
                return {x: pandas.DataFrame.from_records(y) for x, y in response.items()}
            return response
        else:
            print("Check format of your input.")

    @staticmethod
    def cal_candles_base(interval=1, symbol=None, fakeServer=False, strategy_function=None):
        returning_data = {}
        slp = .1
        symbols = FData.all_symbols
        current_dict = {sym: [] for sym in symbols}
        candle_start_time = datetime.now().time()
        next_candle_time = datetime.now().time()
        next_candle_marker = False
        timestamp_format = '%Y-%m-%d %H:%M:%S'
        if fakeServer is True:
            slp = 0
            if symbol is None:
                symbol = 'BANKNIFTY-I'
                input("No symbol was provided, to proceed with BANKNIFTY press any key.\n")
            try:
                df = FData.get_historical(symbol, df=True)
                df['time']
            except KeyError:
                duration = int(input(
                    "Exception Occurred, Seems like market has been closed since yesterday, "
                    "please enter the number of days you want to go back:\n"))
                df = FData.get_historical(symbol, df=True, duration=duration)
            df['time'] = pandas.to_datetime(df['time'], format='%a, %d %b %Y %H:%M:%S %Z')
            df['time'] = df['time'].dt.strftime(timestamp_format)
            df['time'] = pandas.to_datetime(df['time'], format=timestamp_format)
            df.set_index('time', inplace=True)
            df.sort_index(inplace=True)
            NN = df.index[0].replace(second=55, minute=14, hour=9)
            NN = NN.strftime(timestamp_format)
            NN = datetime.strptime(NN, timestamp_format)
            candle_start_time = NN  # DL
            data = FData.get_tick_data()
        while True:
            if fakeServer is False:
                data = FData.get_tick_data()
            for key in symbols:
                if fakeServer is True:  # DLT
                    data[key]['timestamp'] = NN.strftime(timestamp_format)  # DLT
                    data[key]['ltp'] = abcd(NN, df)
                if data[key]['timestamp'] is None:
                    print("Timestamp is None, because market is closed.")
                    break
                current_ltp_time = datetime.strptime(data[key]['timestamp'], timestamp_format)
                # print("Current LTP Time: ", current_ltp_time)
                if candle_start_time.minute != current_ltp_time.minute and next_candle_time.minute != current_ltp_time.minute:
                    current_dict[key].append(data[key]['ltp'])
                    if next_candle_marker is False:
                        next_candle_time = current_ltp_time + timedelta(minutes=interval)
                        next_candle_marker = True
                    # print(f"L1- > {candle_start_time} | {current_ltp_time} | {next_candle_time} | {len(current_dict[key])} | {data[key]['ltp']}")
                elif next_candle_marker is True and next_candle_time.minute == current_ltp_time.minute:
                    candle_start_time = current_ltp_time - timedelta(minutes=interval)
                    next_candle_marker = False
                    next_candle_time = current_ltp_time + timedelta(minutes=interval)
                    try:
                        open_ = current_dict[key][0]
                        high_ = max(current_dict[key])
                        low_ = min(current_dict[key])
                        close_ = current_dict[key][-1]
                    except TypeError as e:
                        print("TypeError occurred")
                        del current_dict[key]
                        symbols.remove(key)
                        FData.all_symbols.remove(key)
                        break
                    timestamp_ = candle_start_time.strftime(timestamp_format)
                    returning_data[key] = {'Timestamp': timestamp_, 'Open': open_,
                                           'High': high_,
                                           'Low': low_, 'Close': close_}
                    FData.candles[key] = {'Timestamp': timestamp_, 'Open': open_,
                                          'High': high_,
                                          'Low': low_, 'Close': close_}
                    if strategy_function is None:
                        FData.candles[key] = {'Timestamp': timestamp_, 'Open': open_,
                                              'High': high_,
                                              'Low': low_, 'Close': close_}

                    current_dict[key].clear()
                    if next_candle_time.second == current_ltp_time.second:
                        current_dict[key].append(data[key]['ltp'])
                else:
                    print(f"Waiting for the minute to end: {current_ltp_time}")
                if current_ltp_time.hour >= 15 and current_ltp_time.minute > 30:
                    return "Market Over"
            if len(FData.candles) > 0:
                print(FData.candles, "FData.all_symbols-> ", FData.all_symbols)
                print("returning_data-> ", returning_data)
            if fakeServer is True:  # DLT
                NN = NN + timedelta(seconds=1)
            if callable(strategy_function) is True and len(returning_data) > 0:
                strategy_function(returning_data)
                returning_data = {}
                """marker = True
                if marker is True:
                    returning_data = {}
                    marker = False"""
            time.sleep(slp)

    def calculate_candles(self, interval=1, symbol=None, fakeServer=False, strategy_function=None):
        if fakeServer is True:
            self.cal_candles_base(strategy_function=strategy_function, interval=interval, symbol=symbol,
                                  fakeServer=fakeServer)
        else:
            thread = threading.Thread(target=self.cal_candles_base, args=(interval, symbol, fakeServer))
            thread.start()
            while True:
                if len(FData.candles) == len(FData.all_symbols):
                    # print(FData.candles)
                    strategy_function(FData.candles)
                    # FData.candles = {}

    def candle(self, sym=None, interval=1, dtype='df'):
        returning_data = {}
        if sym is None:
            sym = list(self.all_symbols)
        res = FData.get_historical(sym, df=True)
        if isinstance(res, dict):
            for x in res:
                #print(x, len(res[x]))
                returning_data[x] = make_candle(res[x], interval, dtype)
                returning_data[x].reset_index(inplace=True)
        if isinstance(res, pandas.DataFrame):
            returning_data[sym] = make_candle(res, interval, dtype)
        return returning_data

    @staticmethod
    def get_candles(passed_func=None):
        while True:
            try:
                data = requests.get(FData.base_url + '/gettickdata', headers=FData.headers)
                tick_data = data.json()
                filtered_data = {sym_dict['symbol']: sym_dict for sym_dict in tick_data if
                                 sym_dict['symbol'] in FData.all_symbols}
                if passed_func == None:
                    return filtered_data
                passed_func(filtered_data)
            except requests.exceptions.JSONDecodeError as e:
                print("Json Error Occurred")
            except TypeError:
                print(f"Type error occurred, this is the Tickdata-> {tick_data}")
                raise Exception

    def get_last_candles(self, sym=None, interval=1, size=5):
        returning_data = {}
        jsn = {}
        jsn['Size'] = size
        jsn['interval'] = interval
        if sym is None:
            sym = list(self.all_symbols)
        if isinstance(sym, list):
            for x in sym:
                jsn['Symbol'] = x
                data = requests.get(FData.base_url + '/dta', headers=FData.headers, json=jsn)
                data = data.json()[0]
                data['time'] = datetime.strptime(data['time'], '%a, %d %b %Y %H:%M:%S %Z').strftime("%Y-%m-%d %H:%M:%S")
                returning_data[x] = data
        else:
            jsn['Symbol'] = sym
            data = requests.get(FData.base_url + '/dta', headers=FData.headers, json=jsn)
            returning_data[sym] = data.json()[0]
        return returning_data
