import uuid


class Chunk:
    def __init__(self, client, body):
        self.id = uuid.uuid4().hex
        self.client = client
        self.body = body
        self.result = None

    def __repr__(self):
        return f'(id = {self.id}, client = {self.client}, body = {self.body})'


class ChunkStorage:
    chunks = set()
    clients_chunk = {}

    @staticmethod
    def register_chunk(chunk):
        ChunkStorage.chunks.add(chunk)
        ChunkStorage.clients_chunk[chunk.client] = chunk
    
    @staticmethod
    def unregister_chunk(chunk):
        ChunkStorage.chunks.remove(chunk)
        ChunkStorage.clients_chunk.pop(chunk.client)


#ChunkStorage.register_chunk(Chunk(client = 1, body = 2))

#print(ChunkStorage.chunks)

# chunk1 = Chunk(client = "Dimas", body = "Dimas_results")
# chunk2 = Chunk(client = "Igor", body = "Igor_results")

# register_chunk(chunk1, chunks, clients_chunk)
# register_chunk(chunk2, chunks, clients_chunk)

# print(chunks)

# unregister_chunk(chunk1, chunks, clients_chunk)
# unregister_chunk(chunk2, chunks, clients_chunk)
