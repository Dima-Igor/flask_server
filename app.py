from logging import debug
from flask import Flask, render_template, url_for, redirect, session, request
from flask_socketio import SocketIO, send


app = Flask(__name__)

socketio = SocketIO(app, cors_allowed_origins='*')

@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('message')
def handle_message(data):
    print(f"Received {data}")
    send(data, broadcast=True)


if __name__ == '__main__':
    socketio.run(app, debug=True)
