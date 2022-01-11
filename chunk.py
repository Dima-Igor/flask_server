import uuid

chunks = set()
clients_chunk = {}

class Chunk:
    def __init__(self, client, body):
        self.id = uuid.uuid4().hex
        self.client = client
        self.body = body

    def __repr__(self):
        return f'(id = {self.id}, client = {self.client}, body = {self.body})'


def register_chunk(chunk, chunks, clients_chunk):
    chunks.add(chunk)
    clients_chunk[chunk.client] = chunk

def unregister_chunk(chunk, chunks, clients_chunk):
    chunks.remove(chunk)
    clients_chunk.pop(chunk.client)


# chunk1 = Chunk(client = "Dimas", body = "Dimas_results")
# chunk2 = Chunk(client = "Igor", body = "Igor_results")

# register_chunk(chunk1, chunks, clients_chunk)
# register_chunk(chunk2, chunks, clients_chunk)

# print(chunks)

# unregister_chunk(chunk1, chunks, clients_chunk)
# unregister_chunk(chunk2, chunks, clients_chunk)
