import uuid

class Chunk:
    def __init__(self, client, body, task_id):
        self.id = uuid.uuid4().hex
        self.client = client
        self.body = body
        self.result = None
        self.task_id = task_id

    def __repr__(self):
        return f'(id = {self.id}, client = {self.client}, body = {self.body}, result = {self.result})'


class ChunkStorage:
    chunks = []

    @staticmethod
    def register_chunk(chunk):
        ChunkStorage.chunks.append(chunk)
        return chunk.id

    @staticmethod
    def complete_chunk(chunk_id, result):
        for chunk in ChunkStorage.chunks:
            if chunk.id == chunk_id:
                chunk.result = result
                break

    @staticmethod
    def complete_task(task_id):
        result_chunks = [
            chunk.result for chunk in ChunkStorage.chunks if chunk.task_id == task_id]
        ChunkStorage.chunks = [
            chunk for chunk in ChunkStorage.chunks if chunk.task_id != task_id]
        return result_chunks

    @staticmethod
    def is_task_completed(task_id):
        for chunk in ChunkStorage.chunks:
            if chunk.task_id == task_id and not chunk.result:
                return False
        return True

    @staticmethod
    def change_client(prev_sid, cur_sid):
        need_to_send_chunks = []
        for chunk in ChunkStorage.chunks:
            if chunk.client == prev_sid and not chunk.result:
                chunk.client = cur_sid
                need_to_send_chunks.append(chunk)
        
        return need_to_send_chunks

    @staticmethod
    def get_task_id(chunk_id):
        task_id = None
        for chunk in  ChunkStorage.chunks:
            if chunk.id == chunk_id:
                task_id = chunk.task_id
                break
        return task_id


#ChunkStorage.register_chunk(Chunk(client = 1, body = 2))

# print(ChunkStorage.chunks)

# chunk1 = Chunk(client = "Dimas", body = "Dimas_results")
# chunk2 = Chunk(client = "Igor", body = "Igor_results")

# register_chunk(chunk1, chunks, clients_chunk)
# register_chunk(chunk2, chunks, clients_chunk)

# print(chunks)

# unregister_chunk(chunk1, chunks, clients_chunk)
# unregister_chunk(chunk2, chunks, clients_chunk)
