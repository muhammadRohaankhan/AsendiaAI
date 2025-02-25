import os
import time
import datetime
import pandas as pd 
import concurrent.futures
from utils.config import load_config
from utils.logger import setup_logger
from database.db_manager import DBManager
from vectordb.vector_index import VectorIndex
from utils.resume_indexer import index_csv_resumes, index_pdf_resumes
from utils.llm_utils import expand_query, rerank_results, generate_summary
from vectordb.precomputed_filter import get_precomputed_indices, bm25_filter, tfidf_filter


os.environ["TOKENIZERS_PARALLELISM"] = "false"

def process_candidate(candidate, query):
    """
    Helper function to process a candidate: generate a summary by appending the query.
    Candidate is a dict with keys: CandidateID, Name, ResumeText.
    Returns the candidate dict with an additional "Summary" field.
    """
    summary = generate_summary(candidate["ResumeText"], query)
    candidate["Summary"] = summary
    return candidate

def main():
    logger = setup_logger()  # logger now logs only to file (see utils/logger.py)
    logger.info("Application started.")

    db_manager = DBManager()
    vector_index = VectorIndex()

    config = load_config()
    
    csv_path = config.get("csv_path", "resumes/resume_data.csv")
    pdf_folder = config.get("pdf_folder", "resumes/")
    
    # Comment these lines when you are done with first time usage:
    index_csv_resumes(csv_path, db_manager, vector_index, logger)
    index_pdf_resumes(pdf_folder, db_manager, vector_index, logger)

    original_query = input("Enter your query: ")  # Taking user input
    logger.info(f"Received query: {original_query}")

    # Expand the query using LLM.
    # Expected output example: {"expanded_query": "<expanded query>", "total_resume": 5}
    expanded_query_output = expand_query(original_query)
    logger.info(f"Expanded query output: {expanded_query_output}")

    # Extract values from the expanded query output
    expanded_query_value = expanded_query_output.get("expanded_query", original_query)
    total_resume_required = expanded_query_output.get("total_resume", 5)
    logger.info(f"Expanded query: {expanded_query_value}")
    logger.info(f"Total resumes required: {total_resume_required}")

    # Retrieve candidates from the database
    all_candidates = db_manager.get_all_candidates()
    candidate_ids = [record[0] for record in all_candidates]
    resume_texts = [record[1] for record in all_candidates]
    total_docs = len(resume_texts)

    # Precompute (or load) BM25 and TF–IDF indices if needed
    bm25, tfidf_vectorizer, tfidf_matrix = get_precomputed_indices(resume_texts, logger)

    # Apply BM25 filtering (select top 10% documents)
    bm25_indices = bm25_filter(expanded_query_value, bm25, total_docs, logger, top_percentage=0.1)
    
    # Apply TF–IDF filtering (select top 10% documents)
    tfidf_indices = tfidf_filter(expanded_query_value, tfidf_vectorizer, tfidf_matrix, total_docs, logger, top_percentage=0.1)
    
    # Combine (union) the indices from both filtering methods
    combined_indices = bm25_indices.union(tfidf_indices)
    filtered_ids = [candidate_ids[i] for i in combined_indices]
    logger.info(f"Filtered candidate IDs (union of BM25 and TF–IDF): {filtered_ids}")
    logger.info(f"Number of filtered candidates: {len(filtered_ids)}")

    # Perform vector search over the entire FAISS index
    vector_results = vector_index.search(expanded_query_value, top_n=10)
    logger.info(f"Vector search results: {vector_results}")

    # Keep only candidates that appear in the prefiltered union
    matched_ids = [cid for cid in vector_results if cid in filtered_ids]
    logger.info(f"Matched CandidateIDs after filtering: {matched_ids}")

    # Re-rank the matched candidates using LLM
    final_results = rerank_results(original_query, matched_ids)
    logger.info(f"Final ranked CandidateIDs before limiting: {final_results}")

    # Limit final results to the number specified in total_resume_required
    final_results = final_results[:total_resume_required]
    logger.info(f"Final ranked CandidateIDs after limiting to {total_resume_required}: {final_results}")

    # Prepare candidate data for parallel summary generation
    candidates_data = []
    for cid in final_results:
        candidate = db_manager.get_candidate_by_id(cid)  # candidate is (CandidateID, Name, ResumeText)
        candidates_data.append({
            "CandidateID": cid,
            "Name": candidate[1],
            "ResumeText": candidate[2]
        })

    # Run summary generation in parallel with 5 processes.
    start_time = time.time()
    with concurrent.futures.ProcessPoolExecutor(max_workers=5) as executor:
        # Pass the top-level process_candidate function along with a repeated original_query.
        processed_candidates = list(executor.map(process_candidate, candidates_data, [original_query] * len(candidates_data)))
    end_time = time.time()
    time_taken = end_time - start_time
    logger.info(f"Time taken for summary generation (parallel with 5 processes): {time_taken:.2f} seconds")

    # Prepare data for Excel output
    output_data = processed_candidates

    # Create an output folder if it doesn't exist
    output_folder = "output"
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Create a unique filename using timestamp
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    output_file = os.path.join(output_folder, f"resume_output_{timestamp}.xlsx")

    # Save the candidate summaries and details to an Excel file
    df = pd.DataFrame(output_data)
    df.to_excel(output_file, index=False)
    logger.info(f"Output saved to {output_file}")

    logger.info("Query processing complete. Application finished.")

if __name__ == "__main__":
    main()
