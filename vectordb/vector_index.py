# Updated vector_index.py
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
import os
import json

class VectorIndex:
    def __init__(self, dimension: int = 384, index_path='faiss.index', mapping_path='candidate_ids.json'):
        """
        Initialize the vector index using Sentence-BERT and FAISS.
        If a persisted index exists, load it.
        """
        self.dimension = dimension
        self.index_path = index_path
        self.mapping_path = mapping_path
        self.model = SentenceTransformer('all-MiniLM-L6-v2')
        self.candidate_ids = []
        
        if os.path.exists(self.index_path) and os.path.exists(self.mapping_path):
            # Load the persisted FAISS index and candidate IDs
            self.index = faiss.read_index(self.index_path)
            with open(self.mapping_path, 'r') as f:
                self.candidate_ids = json.load(f)
        else:
            # Create a new FAISS index
            self.index = faiss.IndexFlatL2(dimension)

    def add_candidate(self, candidate_id: str, resume_text: str):
        """
        Generate an embedding for the resume text and add it to the FAISS index.
        The candidate is added to the candidate_ids list, and the index is persisted.
        """
        embedding = self.model.encode([resume_text])
        embedding = np.array(embedding).astype('float32')
        self.index.add(embedding)
        self.candidate_ids.append(candidate_id)
        self.save()  # Persist changes after each addition

    def save(self):
        """
        Save the FAISS index and candidate_ids mapping to disk.
        """
        faiss.write_index(self.index, self.index_path)
        with open(self.mapping_path, 'w') as f:
            json.dump(self.candidate_ids, f)

    def search(self, query: str, top_n: int = 5) -> list:
        """
        Generate an embedding for the query and perform a vector search.
        Returns the top N matching CandidateIDs.
        """
        query_embedding = self.model.encode([query])
        query_embedding = np.array(query_embedding).astype('float32')
        distances, indices = self.index.search(query_embedding, top_n)
        results = []
        for idx in indices[0]:
            if idx < len(self.candidate_ids):
                results.append(self.candidate_ids[idx])
        return results
