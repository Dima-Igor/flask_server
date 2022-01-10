from logging import debug
from flask import Flask, render_template, url_for, redirect, session, request
from flask_socketio import SocketIO, send
import json

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

clients = set()


@socketio.on('connect')
def handle_connect():
    print('Client connected')
    clients.add(request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')
    clients.remove(request.sid)


def send_message(event_name, client_id, data):
    socketio.emit(event_name, data, room=client_id)
    print(f'sending message "{data}" to client "{client_id}".')


@app.route('/')
def index():
    return render_template('index.html')


@socketio.on('message')
def handle_message(data):
    print(f"Received {data} from {request.sid}")
    send(data, broadcast=True)


def get_all_submissions(handle):
    # request to cf api
    return [{'handle': 'igor', 'kek': 'lol'}, {'handle': 'kwerwerw'}]


def split_submissions(submissions, clients_count):
    pass


@app.post('/make_task')
def make_task():

    json_data = request.get_json()

    handle = json_data['handle']
    sid = json_data['sid']

    submissions = get_all_submissions(handle)
    #clients_count = 2
    #submission_chunks = split_submissions(submissions, clients_count)

    print(handle, sid)
    # print(jsonify(submissions))

    for client_id in clients:
        send_message('run_task', client_id=client_id, data=client_id)

    return "1", 200

    #send(jsonify(submissions), broadcast=True)

    #socketio.emit('task', jsonify(submissions))

    # for chunk, client in zip(submission_chunks, clients):
    # socketio.send()


if __name__ == '__main__':
    socketio.run(app, debug=True)
