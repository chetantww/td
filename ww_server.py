import logging
from datetime import datetime, timedelta, datetime as dt
from functools import wraps
import time
import jwt
from flask import Flask, request, jsonify, make_response
from truedata_ws.websocket.TD import TD


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
                              url=self.url, log_level=logging.INFO, log_format="%(message)s")
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

    @staticmethod
    def get_histdata(sym, start_time=None, duration=None, end_time=None):
        if start_time != None:
            if end_time != None:
                return TDConnection.obj.get_historic_data(sym, end_time=end_time, start_time=start_time)
            return TDConnection.obj.get_historic_data(sym, start_time=start_time)
        if duration != None:
            duration = str(duration) + ' D'
            return TDConnection.obj.get_historic_data(sym, duration=duration)
        return TDConnection.obj.get_historic_data(sym)

    @staticmethod
    def abc(symbol, min, nBars):
        dta = TDConnection.obj.get_n_historical_bars(symbol, no_of_bars=nBars, bar_size=f'{min} min')
        return dta


app = Flask(__name__)
app.config['SECRET_KEY'] = 'ANytHingSecuRe'
auth_keys = ['trial']
wildcard_key = 'AdMiN@#wWeAlThWiSeRs'
response = {
    'token': None,
    'message': None,
    'auth-status': "Login required",
}


def token_required(function):
    @wraps(function)
    def decorated(*args, **kwargs):
        token = None
        api_response = response.copy()
        if 'token' in request.headers:
            token = request.headers['token']
        if not token:
            api_response['message'] = 'token is missing'
            return jsonify(api_response), 401
        try:
            jwt.decode(token, app.config['SECRET_KEY'], algorithms='HS256')
        except jwt.exceptions.ExpiredSignatureError:
            api_response['message'] = 'token is Expired'
            return jsonify(api_response), 401
        except jwt.exceptions.InvalidSignatureError:
            api_response['message'] = 'token is Invalid'
            return jsonify(api_response), 401
        return function(*args, **kwargs)

    return decorated


@app.route('/', methods=['GET'])
def index():
    api_response = response.copy()
    api_response['message'] = 'Welcome to WealthWisers Server'
    return make_response(jsonify(api_response), 200)


@app.route('/login', methods=['POST', 'GET'])
def login():
    auth = request.headers  # key ip
    api_response = response.copy()
    if not auth or not auth.get('key'):
        api_response['message'] = 'Could not verify'
        api_response['auth-status'] = "Login required"
        return make_response(jsonify(api_response), 401)
    if auth.get('key') in auth_keys:
        token = jwt.encode({
            'public_id': auth.get('ip'),
            'exp': datetime.utcnow() + timedelta(seconds=30, minutes=30)
        }, app.config['SECRET_KEY'], algorithm='HS256')
        api_response['message'] = 'Success'
        api_response['token'] = token
        api_response['auth-status'] = 'Login successful'
        return make_response(jsonify(api_response), 200)
    api_response['message'] = 'Wrong Password'
    api_response['token'] = 'Not Found'
    api_response['auth-status'] = 'Login unsuccessful'
    return make_response(jsonify(api_response), 401)


@app.route('/connect', methods=['POST'])
@token_required
def connect():
    api_response = response.copy()
    api_response['auth-status'] = 'Logged in'
    username = request.json['username']
    password = request.json['password']
    port = request.json['port']
    url = request.json['url']
    if request.method == 'POST':
        if not username or not password or not port or not url:
            api_response['message'] = "Invalid format."
            status = 400
        elif TDConnection.connection_status is False:
            # TDConnection('tdwsp353', 'anjan@353', 8082, 'push.truedata.in').connect()
            TDConnection(username=username, password=password, realtime_port=port, url=url).connect()
            TDConnection.connection_status = True
            api_response['message'] = "Connected to Wealthwisers' Server."
            status = 200
        else:
            api_response['message'] = "Already connected to Wealthwisers' Server."
            status = 200
    else:
        api_response['message'] = "Uknown Request."
        status = 405
    return make_response(jsonify(api_response), status)


@app.route('/disconnectt', methods=['POST'])
@token_required
def disconnect():
    api_response = response.copy()
    status = 400
    if request.headers.get('key') == wildcard_key:
        if request.method == 'POST' and TDConnection.connection_status is True:
            TDConnection.disconnect()
            TDConnection.connection_status = False
            api_response['message'], status = "Disconnected from Wealthwisers' Server.", 200
    else:
        api_response['message'], status = "Unknown request, or you are not authorized to disconnect.", 200
    return make_response(jsonify(api_response), status)


@app.route('/ticksymbols', methods=['POST', 'GET'])
@token_required
def add_symbols():
    api_response = response.copy()
    symbol = request.json['Symbols']
    if request.method == 'POST':
        api_response['message'], status = TDConnection.TickData(symbol=symbol), 200
    elif request.method == 'GET':
        api_response['message'], status = list(TDConnection.tick_symbols), 200
    else:
        api_response['message'], status = "Invalid format.", 405
    return make_response(jsonify(api_response), status)


@app.route('/ocsymbols', methods=['POST', 'GET'])
@token_required
def add_optionchain_symbols():
    api_response = response.copy()
    symbols = request.json
    symbols = symbols['Symbols']
    api_response['message'], status = "Unknown request", 401
    if request.method == 'POST':
        final_syms = ''
        if isinstance(symbols, list):
            for symbol in symbols:
                sym = TDConnection.OptionChain(**symbol)
                final_syms += sym + ','
            api_response['message'], status = f"Symbols added are, {final_syms[:-1]}", 200
        else:
            api_response['message'], status = "Invalid format.", 405
    if request.method == 'GET':
        api_response['message'], status = f"Symbols are, {list(TDConnection.option_chain_symbols)}", 200

    return make_response(jsonify(api_response), status)


@app.route('/gettickdata')
@token_required
def gettickdata():
    return make_response(jsonify(TDConnection.get_tick_data()), 200)





@app.route('/debug', methods=['GET', 'POST'])
def a():
    if TDConnection.connection_status is False:
        TDConnection('tdwsp353', 'anjan@353', 8082, 'push.truedata.in').connect()
        TDConnection.connection_status = True
        time.sleep(1)
    TDConnection.TickData(symbol=['BANKNIFTY-I'])
    return make_response(jsonify(TDConnection.get_tick_data()), 200)


@app.route('/getocdata', methods=['GET'])
@token_required
def getod():
    return make_response(jsonify(TDConnection.get_option_chain_data()), 200)


@app.route('/histdata', methods=['GET'])
@token_required
def histdata():
    if 'Symbol' in request.json:
        sym = request.json['Symbol']
        start, duration, end = request.json['Start'], request.json['Duration'], request.json['End']
        start = [dt.strptime(start, '%Y-%m-%d') if start is not None else start][0]
        end = [dt.strptime(end, '%Y-%m-%d') if end is not None else end][0]
        duration = [int(duration) if duration is not None else duration][0]
        if isinstance(sym, str):
            return make_response(jsonify(TDConnection.get_histdata(sym, start, duration, end)), 200)


@app.route('/dta', methods=['POST', 'GET'])
@token_required
def dta():
    sym = request.json['Symbol']
    nBars = request.json['Size']
    min = request.json['interval']
    return make_response(jsonify(TDConnection.abc(sym, min=min, nBars=nBars)), 200)


if __name__ == '__main__':
    app.run(port=5555)



