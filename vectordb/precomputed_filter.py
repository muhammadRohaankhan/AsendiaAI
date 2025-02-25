import os
import pickle
import numpy as np
from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

PRECOMPUTED_FILE = 'precomputed_filter.pkl'

def compute_indices(resume_texts, logger):
    """
    Compute BM25 and TF–IDF indices from the resume_texts.
    """
    # Tokenize each document for BM25
    tokenized_corpus = [doc.split() for doc in resume_texts]
    bm25 = BM25Okapi(tokenized_corpus)

    # Compute TF–IDF representation
    tfidf_vectorizer = TfidfVectorizer()
    tfidf_matrix = tfidf_vectorizer.fit_transform(resume_texts)
    
    logger.info("Computed BM25 and TF–IDF indices.")
    return bm25, tfidf_vectorizer, tfidf_matrix

def load_precomputed_indices(logger):
    if os.path.exists(PRECOMPUTED_FILE):
        with open(PRECOMPUTED_FILE, 'rb') as f:
            data = pickle.load(f)
        logger.info("Loaded precomputed indices from disk.")
        return data
    else:
        logger.info("No precomputed indices file found.")
        return None

def save_precomputed_indices(data, logger):
    with open(PRECOMPUTED_FILE, 'wb') as f:
        pickle.dump(data, f)
    logger.info("Saved precomputed indices to disk.")

def get_precomputed_indices(resume_texts, logger):
    """
    Returns the precomputed BM25, TF–IDF vectorizer, and TF–IDF matrix.
    Recompute only if:
      1) There is no existing precomputed file, or
      2) The number of resumes has changed.
    """
    data = load_precomputed_indices(logger)
    current_doc_count = len(resume_texts)
    if data and data.get("doc_count") == current_doc_count:
        return data["bm25"], data["tfidf_vectorizer"], data["tfidf_matrix"]
    else:
        logger.info("Precomputed indices are outdated or not available. Recomputing...")
        bm25, tfidf_vectorizer, tfidf_matrix = compute_indices(resume_texts, logger)
        data = {
            "doc_count": current_doc_count,
            "bm25": bm25,
            "tfidf_vectorizer": tfidf_vectorizer,
            "tfidf_matrix": tfidf_matrix
        }
        save_precomputed_indices(data, logger)
        return bm25, tfidf_vectorizer, tfidf_matrix

def bm25_filter(query, bm25, total_docs, logger, top_percentage=0.1):
    """
    Compute BM25 scores for the query and return indices of the top percentage of documents.
    """
    tokenized_query = query.split()
    scores = bm25.get_scores(tokenized_query)
    top_k = max(1, int(total_docs * top_percentage))
    top_indices = np.argsort(scores)[::-1][:top_k]
    logger.info(f"BM25 filtering selected indices: {top_indices.tolist()}")
    return set(top_indices.tolist())

def tfidf_filter(query, tfidf_vectorizer, tfidf_matrix, total_docs, logger, top_percentage=0.1):
    """
    Compute cosine similarity using TF–IDF and return indices of the top percentage of documents.
    """
    query_vector = tfidf_vectorizer.transform([query])
    cos_sim = cosine_similarity(query_vector, tfidf_matrix).flatten()
    top_k = max(1, int(total_docs * top_percentage))
    top_indices = np.argsort(cos_sim)[::-1][:top_k]
    logger.info(f"TF–IDF filtering selected indices: {top_indices.tolist()}")
    return set(top_indices.tolist())
