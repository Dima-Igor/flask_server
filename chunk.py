import uuid


class Chunk:
    def __init__(self, client, body, task_id):
        self.id = uuid.uuid4().hex
        self.client = client
        self.body = body
        self.result = None
        self.task_id = task_id

    def __repr__(self):
        return f'(id = {self.id}, client = {self.client}, body = {self.body})'


class ChunkStorage:
    chunks = []

    @staticmethod
    def register_chunk(chunk):
        ChunkStorage.chunks.add(chunk)
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
    def change_client(chunk_id, sid):
        for chunk in ChunkStorage.chunks:
            if chunk.id == chunk_id:
                chunk.client = sid
                break


#ChunkStorage.register_chunk(Chunk(client = 1, body = 2))

# print(ChunkStorage.chunks)

# chunk1 = Chunk(client = "Dimas", body = "Dimas_results")
# chunk2 = Chunk(client = "Igor", body = "Igor_results")

# register_chunk(chunk1, chunks, clients_chunk)
# register_chunk(chunk2, chunks, clients_chunk)

# print(chunks)

# unregister_chunk(chunk1, chunks, clients_chunk)
# unregister_chunk(chunk2, chunks, clients_chunk)
