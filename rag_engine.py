import os
import json
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

INDEX_PATH = "vector_store/vector.index"
DOC_STORE = "vector_store/documents.jsonl"


class RAGEngine:

    def __init__(self):
        self.model = SentenceTransformer("all-MiniLM-L6-v2")
        self.index = None
        self.documents = []

        # Load documents
        if os.path.exists(DOC_STORE):
            with open(DOC_STORE, "r", encoding="utf-8") as f:
                self.documents = [json.loads(line)["text"] for line in f]

        # Load FAISS index
        if os.path.exists(INDEX_PATH):
            self.index = faiss.read_index(INDEX_PATH)

    # -----------------------------
    # BUILD INDEX (incremental)
    # -----------------------------
    def build_index(self, new_docs):
        # Persist new docs
        with open(DOC_STORE, "a", encoding="utf-8") as f:
            for d in new_docs:
                f.write(json.dumps({"text": d}) + "\n")

        self.documents.extend(new_docs)

        # Encode only new docs
        new_embeddings = self.model.encode(new_docs)
        new_embeddings = np.array(new_embeddings)

        # Initialize index if needed
        if self.index is None:
            dim = new_embeddings.shape[1]
            self.index = faiss.IndexFlatL2(dim)

        # Add new vectors
        self.index.add(new_embeddings)

        # Save index
        faiss.write_index(self.index, INDEX_PATH)

    # -----------------------------
    # RETRIEVE
    # -----------------------------
    def retrieve(self, query, k=5):
        if self.index is None or not self.documents:
            return []

        q_embed = self.model.encode([query])
        q_embed = np.array(q_embed)

        _, idx = self.index.search(q_embed, k)

        return [
            self.documents[i]
            for i in idx[0]
            if 0 <= i < len(self.documents)
        ]
