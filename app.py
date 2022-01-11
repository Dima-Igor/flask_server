from logging import debug
from flask import Flask, render_template, url_for, redirect, session, request, jsonify, make_response
from flask_socketio import SocketIO, send
import json
import submission_pb2_grpc
import submission_pb2
import grpc
from rabbit_scheduler import RabbitMQScheduler
from itertools import islice
import time

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

clients = set()
cf_service_addr = "localhost:8090"
grpc_channel = grpc.insecure_channel(cf_service_addr)


#mq_scheduler = RabbitMQScheduler()


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


def get_all_submissions(handle):
    stub = submission_pb2_grpc.CodeforcesServiceStub(grpc_channel)
    responses = stub.GetSubmissions(
        submission_pb2.SubmissionRequest(handle=handle))

    submissions = []
    amount = 0

    try:
        for response in responses:
            # TODO - check is user not found and other errors
            if (response.status != "OK"):
                print(response.status)

            submissions.append({
                'contest_id': response.contest_id,
                'problem_index': response.problem_index,
                'sub_time': response.sub_time,
                'verdict': response.verdict,
                'rating': response.problem_rating
            })

            amount += 1
    except grpc.RpcError as rpc_error:
        print(rpc_error.code())

    print(amount)
    return submissions


def chunks(l, n):
    """Yield n number of sequential chunks from l."""
    d, r = divmod(len(l), n)
    for i in range(n):
        si = (d+1)*(i if i < r else r) + d*(0 if i < r else i - r)
        yield l[si:si+(d+1 if i < r else d)]


def split_submissions(submissions, clients_count):
    return list(chunks(submissions, clients_count))


@socketio.on('add_task')
def add_task(data):
    json_data = data

    print(f"Add task with data : {json_data}")

    handle = json_data['handle']
    sid = request.sid
    print(handle,sid)

    task = {}
    task['handle'] = handle
    task['sid'] = sid
    
    #mq_scheduler.send_task(task)

    return make_response("", 200)


@app.post('/make_task')
def make_task():
    json_data = request.get_json()

    print(f"Make task with data : {json_data}")

    handle = json_data['handle']
    sid = json_data['sid']

    # handle if we didn't get any submisisons
    submissions = get_all_submissions(handle)

    clients_count = min(len(clients), len(submissions))
    submission_chunks = split_submissions(submissions, clients_count)

    print(clients_count)

    for i, client_id in enumerate(clients):
        if i >= clients_count:
            break
        send_message('run_task', client_id=client_id,
                     data=json.dumps(submission_chunks[i]))

    # пока не обработаны все блоки
    global completed_chunks

    completed_chunks = 0
    while(completed_chunks < len(submission_chunks)):
        waiting = 1

    



    # submissions = get_all_submissions(handle)
    # for client_id in clients:
    #     send_message('run_task', client_id=client_id,
    #                  data=json.dumps(submissions))
    #     send_message('run_task', client_id=client_id, data=client_id)

    return make_response("", 200)


if __name__ == '__main__':
    socketio.run(app, debug=True)
