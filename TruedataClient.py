from truedata_ws.websocket.TD import TD
import logging
from datetime import datetime as dt

"""username = 'tdwsp353'
password = 'anjan@353'
realtime_port = 8082
url = 'push.truedata.in'
TDConnection = TD(username, password, live_port=realtime_port, url=url, log_level=logging.WARNING, log_format="%(message)s")
req_ids = TDConnection.start_live_data(['BANKNIFTY-I'])  # ["BANKNIFTY-I"]
time.sleep(1)
"""

class TDConnection:
    connection_status = False
    obj = None
    option_chain_dict = {}
    tick_symbols = set()
    option_chain_symbols = set()
    req_ids = []

    def __init__(self, username, password, realtime_port, url):
        self.username = username
        self.password = password
        self.realtime_port = realtime_port
        self.url = url

    def connect(self):
        TDConnection.obj = TD(self.username, self.password, live_port=self.realtime_port,
                              url=self.url, log_level=logging.WARNING, log_format="%(message)s")
        self.connection_status = True

    @staticmethod
    def disconnect():
        TDConnection.obj.disconnect()
        TDConnection.obj = None
        TDConnection.connection_status = False
        return TDConnection.obj

    @staticmethod
    def OptionChain(symbol=None, expiry_year=None, expiry_month=None, expiry_day=None):
        assert symbol is not None and expiry_year is not None and expiry_month is not None and expiry_day is not None, "Invalid input for Option chain."
        symbol = symbol
        option_chain_obj = TDConnection.obj.start_option_chain(symbol,
                                                               dt(expiry_year, expiry_month, expiry_day),
                                                               chain_length=50, bid_ask=True)

        final_sym = symbol + str(expiry_year) + str(expiry_month) + str(expiry_day)
        TDConnection.option_chain_dict[final_sym] = option_chain_obj
        TDConnection.option_chain_symbols.add(final_sym)
        return final_sym

    @staticmethod
    def get_option_chain_data():
        financial_data = {}
        for key, val in TDConnection.option_chain_dict.items():
            data = val.get_option_chain()
            data['ltt'] = data['ltt'].astype(str)
            financial_data[key] = data.to_dict()
        return financial_data

    @staticmethod
    def TickData(symbol=None):
        assert symbol is not None, "Invalid input"
        if isinstance(symbol, list):
            TDConnection.tick_symbols.update(symbol)
            TDConnection.req_ids = TDConnection.obj.start_live_data(list(TDConnection.tick_symbols))
            return f"Symbols added are, '{str(symbol)[1:-1]}'."
        if isinstance(symbol, str):
            TDConnection.tick_symbols.add(symbol)
            TDConnection.req_ids = TDConnection.obj.start_live_data(list(TDConnection.tick_symbols))
            return f"Symbols added is '{str(symbol)}'."

    @staticmethod
    def get_tick_data(debug=False):
        financial_data = []
        for req_id in TDConnection.req_ids:
            data = TDConnection.obj.live_data[req_id].to_dict()
            if debug is True:
                print(data)
            if isinstance(data['timestamp'], dt):
                data['timestamp'] = data['timestamp'].strftime(format="%Y-%m-%d %H:%M:%S")
            financial_data.append(data)
        return financial_data


while TDConnection.connection_status is True:
    pass