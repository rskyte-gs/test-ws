from flask import Flask, render_template, request, redirect, make_response
from flask_socketio import SocketIO, emit
import logging
import os

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

games = {}

socketURL = os.getenv('SOCKETURL')
dev_mode = os.getenv('DEVMODE') == 'True'
host = '0.0.0.0'
if dev_mode is True:
    host = socketURL[7:-5]   

def render_view(viewname, params):
    return render_template(viewname, **params)

@app.route('/')
def index():
    return render_view('index.html', {})

@app.route('/games/create', methods=['GET'])
def game_form():
    return render_view('create_game.html', {})

@app.route('/games/create', methods=['POST'])
def create_game():
    name = request.form['game_name']
    while name in games.keys():
        num = 1
        if name[-1] in ['1','2','3','4','5','6','7','8','9']:
            num = int(name[-1])
            num += 1
        name += str(num)
    games[name] = {
        'slider1': 25,
        'slider2': 0
    }
    resp = make_response(redirect('/games/all'))
    return resp

@app.route('/games/all')
def list_game():
    return render_view('game_list.html', { 'games': games })

@app.route('/games/<game_name>')
def join_game(game_name):
     return render_view('game.html', { 'slider1': games[game_name]['slider1'], 'slider2': games[game_name]['slider2'], 'game': game_name, 'socketURL': socketURL })

@socketio.on('connect')
def test_connect():
    emit('after connect', { 'data': 'Let\'s Dance!' })

@socketio.on('Slider value changed')
def value_changed(message):
    games[message['game_name']][message['who']] = message['data']
    emit(message['game_name'] + ' update value', message, broadcast=True)

if __name__ == '__main__':
    socketio.run(app, host=host, port=9000, debug=True)