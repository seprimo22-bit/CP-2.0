import faiss
import numpy as np
import os
from sentence_transformers import SentenceTransformer

INDEX_PATH = "vector_store/vector.index"

class RAGEngine:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.documents = []

        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)

    def build_index(self, docs):
        self.documents.extend(docs)

        embeddings = self.model.encode(self.documents)
        dim = embeddings.shape[1]

        self.index = faiss.IndexFlatL2(dim)
        self.index.add(np.array(embeddings))

        faiss.write_index(self.index, INDEX_PATH)

    def retrieve(self, query, k=5):
        if self.index is None:
            return []

        q_embed = self.model.encode([query])
        _, idx = self.index.search(np.array(q_embed), k)

        return [self.documents[i] for i in idx[0] if i < len(self.documents)]
