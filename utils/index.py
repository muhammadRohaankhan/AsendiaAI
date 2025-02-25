import os
import hashlib
import pandas as pd
from database.db_manager import DBManager
from vectordb.vector_index import VectorIndex
from config import load_config
import logging

config = load_config()

def generate_candidate_id(text: str) -> str:
    """
    Generate a unique candidate ID by hashing the provided text.
    """
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

def index_csv_resumes(csv_path: str, db_manager: DBManager, vector_index: VectorIndex, logger: logging.Logger):
    """
    Process and index resumes from a CSV file.
    Select specific columns, create a concatenated resume text, and insert into the database.
    Only new rows (determined by unique candidate IDs) are processed.
    """
    logger.info("Starting CSV resume indexing.")
    # Read CSV file
    df = pd.read_csv(csv_path)
    
    # Define the columns to select
    selected_columns = [
        "skills", "start_dates", "end_dates", "professional_company_names",
        "educational_institution_name", "degree_names", "passing_years",
        "positions", "responsibilities"
    ]
    
    # Fill missing values with empty strings
    df[selected_columns] = df[selected_columns].fillna("")
    
    for index, row in df.iterrows():
        # Construct resume text by concatenating selected columns with labels
        resume_text = (
            f"skills: {row['skills']}; "
            f"start_dates: {row['start_dates']}; "
            f"end_dates: {row['end_dates']}; "
            f"professional_company_names: {row['professional_company_names']}; "
            f"educational_institution_name: {row['educational_institution_name']}; "
            f"degree_names: {row['degree_names']}; "
            f"passing_years: {row['passing_years']}; "
            f"positions: {row['positions']}; "
            f"responsibilities: {row['responsibilities']}"
        )
        candidate_id = generate_candidate_id(resume_text)
        
        # Check if candidate already exists
        if not db_manager.candidate_exists(candidate_id):
            candidate_data = {
                "CandidateID": candidate_id,
                "ResumeText": resume_text
            }
            db_manager.insert_candidate(candidate_data)
            vector_index.add_candidate(candidate_id, resume_text)
            logger.info(f"Indexed CSV candidate: {candidate_id}")
        else:
            logger.info(f"CSV candidate already exists: {candidate_id}")
    logger.info("Finished indexing CSV resumes.")

def index_pdf_resumes(pdf_folder: str, db_manager: DBManager, vector_index: VectorIndex, logger: logging.Logger):
    """
    Process and index resumes from PDF files in a folder.
    For each PDF, use LLM extraction (via parse_resume) to obtain candidate info.
    Only new candidates (by unique CandidateID) are processed.
    """
    from utils.resume_parser import parse_resume
    logger.info("Starting PDF resume indexing.")
    for filename in os.listdir(pdf_folder):
        if filename.lower().endswith(".pdf"):
            file_path = os.path.join(pdf_folder, filename)
            try:
                # parse_resume converts PDF to text, cleans it, and uses LLM to extract candidate info
                resume_data = parse_resume(file_path)
                candidate_info = resume_data.get("candidate_info", {})
                # Try to get CandidateID from extracted info; if missing, generate one from the text.
                candidate_id = candidate_info.get("candidate", {}).get("CandidateID")
                if not candidate_id:
                    candidate_id = generate_candidate_id(resume_data["text"])
                if not db_manager.candidate_exists(candidate_id):
                    candidate_data = {
                        "CandidateID": candidate_id,
                        "Name": candidate_info.get("candidate", {}).get("Name", ""),
                        "ResumeText": resume_data["text"]
                    }
                    db_manager.insert_candidate(candidate_data)
                    vector_index.add_candidate(candidate_id, resume_data["text"])
                    logger.info(f"Indexed PDF candidate: {filename} as {candidate_id}")
                else:
                    logger.info(f"PDF candidate already exists: {candidate_id}")
            except Exception as e:
                logger.error(f"Failed to process PDF {filename}: {e}")
    logger.info("Finished indexing PDF resumes.")
