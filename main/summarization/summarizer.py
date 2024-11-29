import ollama

class Summarizer:
    def __init__(self):
        pass

    def summarize(self, chunk):
        # summarizes the text chunk
        response = ollama.embeddings(model='orca-mini:7b-q2_K', prompt=chunk)
        return response
