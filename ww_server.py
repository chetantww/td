from datetime import datetime, timedelta
from functools import wraps

import jwt
from flask import Flask, request, jsonify, make_response

from TruedataClient import TDConnection

app = Flask(__name__)
app.config['SECRET_KEY'] = 'ANytHingSecuRe'
auth_keys = ['trial']

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


@app.route('/disconnect', methods=['POST'])
@token_required
def disconnect():
    api_response = response.copy()
    if request.method == 'POST' and TDConnection.connection_status is True:
        TDConnection.disconnect()
        TDConnection.connection_status = False
        api_response['message'], status = "Disconnected from Wealthwisers' Server.", 200
    else:
        api_response['message'], status = "Unknown request.", 200
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


@app.route('/getocdata', methods=['GET'])
@token_required
def getod():
    return make_response(jsonify(TDConnection.get_option_chain_data()), 200)


if __name__ == '__main__':
    app.run(host='http://127.0.0.1', port=5000, debug=True, threaded=True)
