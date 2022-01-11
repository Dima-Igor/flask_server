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
from chunk import ChunkStorage, Chunk
import random
import uuid

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins='*')

clients = set()
cf_service_addr = "localhost:8090"
grpc_channel = grpc.insecure_channel(cf_service_addr)

#for each task store user who want this task
tasks_sid = {}
mq_scheduler = RabbitMQScheduler()

@socketio.on('connect')
def handle_connect():
    print(f'Client {request.sid} connected')
    clients.add(request.sid)


@socketio.on('disconnect')
def handle_disconnect():
    print(f'Client {request.sid} disconnected')

    sid = request.sid   
    clients.remove(request.sid)

    if len(clients) == 0:
        return
    
    prev_client = sid
    if len(clients) == 0:
        return

    #pick random client to run task, if someone disconnected
    cur_client = random.choice(tuple(clients))
    need_to_send = ChunkStorage.change_client(prev_client, cur_client)

    for chunk in need_to_send:
        send_message(event_name = 'run_task', client_id = cur_client, data = chunk)


def send_message(event_name, client_id, data):
    socketio.emit(event_name, data, room=client_id)
    print(f'sending message to client "{client_id}".')


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
                return [False, response.status]

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
        return [False, str(rpc_error.code())]

    print(f"Received {amount} submissions")
    return [True, submissions]

def split_chunks(l, n):
    """Yield n number of sequential chunks from l."""
    d, r = divmod(len(l), n)
    for i in range(n):
        si = (d+1)*(i if i < r else r) + d*(0 if i < r else i - r)
        yield l[si:si+(d+1 if i < r else d)]


def split_submissions(submissions, clients_count):
    return list(split_chunks(submissions, clients_count))


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
    
    mq_scheduler.send_task(task)

    return make_response("", 200)


def merge_results(results):
    stats = {
        'solvedTasks': 0,
        'solvedRatedTasks': 0,
        'averageRating': 0,
        'okCount': 0,
        'waCount': 0,
        'mlCount': 0,
        'tlCount': 0
    }

    
    for result in results:
        stats['solvedTasks']+= result['solvedTasks']
        stats['solvedRatedTasks']+=result['solvedRatedTasks']
        stats['averageRating']+=result['sumRating']
        stats['okCount']+=result['okCount']
        stats['waCount']+=result['waCount']
        stats['mlCount']+=result['mlCount']
        stats['tlCount']+=result['tlCount']

    if stats['solvedRatedTasks'] >0:
        stats['averageRating']/=stats['solvedRatedTasks']

    return stats


@socketio.on('get_task_result')
def get_task_result(data):
    chunk_id = data['chunkId']
    result = data['result']

    print(f" {request.sid} completed chunk {chunk_id}")
    ChunkStorage.complete_chunk(chunk_id, result)
    task_id = ChunkStorage.get_task_id(chunk_id)

    #print(ChunkStorage.chunks[0])

    if ChunkStorage.is_task_completed(task_id):
        results = ChunkStorage.complete_task(task_id)
        stats = merge_results(results)
        if task_id not in tasks_sid:
            return

        requester_sid = tasks_sid[task_id]
        tasks_sid.pop(task_id)
        send_message('draw_stats', requester_sid, data = json.dumps(stats))

    
@app.post('/make_task')
def make_task():
    json_data = request.get_json()

    print(f"Make task with data : {json_data}")
    handle = json_data['handle']
    sid = json_data['sid']


    if sid not in clients:
        return make_response("Client not found",200)
        
    # handle if something went wrong
    status, submissions = get_all_submissions(handle)
    if not status:
        send_message('draw_stats', client_id=sid, data=json.dumps({'error': submissions}))
        return make_response(submissions, 200)

    if not submissions:
        send_message('draw_stats', client_id=sid, data = json.dumps({'error': 'User has no submissions'}))
        return make_response(submissions, 200)

    clients_count = min(len(clients), len(submissions))
    submission_chunks = split_submissions(submissions, clients_count)
    task_id = uuid.uuid4().hex

    #What are we going todo if there are no clients?
    if clients_count == 0:
        return make_response("No clients", 200)

    #for each user need to store their tasks
    tasks_sid[task_id] = sid

    for i, client_id in enumerate(clients):
        if i >= clients_count:
            break
        
        chunk = Chunk(client = client_id, body = submission_chunks[i], task_id = task_id)
        ChunkStorage.register_chunk(chunk)
        send_message('run_task', client_id=client_id,
                     data=json.dumps(
                         {'submissions': submission_chunks[i],
                            'chunk_id': chunk.id}))

    return make_response("OK", 200)


if __name__ == '__main__':
    socketio.run(app, debug=True)
