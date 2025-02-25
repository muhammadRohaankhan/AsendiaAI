Below is an example of a comprehensive **README.md** file for your project:

---

# Asendia Resume Matching System

The Asendia Resume Matching System is a scalable, multi-modal resume retrieval and candidate ranking solution. It leverages traditional text-based search techniques (BM25 and TF–IDF) along with modern embedding-based vector search (using FAISS and SentenceTransformer) and LLM-based re-ranking and summary generation. This project is designed to help recruiters quickly find and evaluate candidates based on a job query.

## Features

- **Resume Indexing:**  
  - Supports CSV resume ingestion.  
  - Uses a SQLite database to store candidate details.
  - Generates unique candidate IDs based on resume content.

- **Text-Based Filtering:**  
  - Precomputes BM25 and TF–IDF representations to filter resumes.
  - Caches these indices for faster repeated queries (updates automatically when new resumes are added).

- **Vector Search:**  
  - Embeds resumes using SentenceTransformer.
  - Uses FAISS for fast similarity search.

- **LLM Re-Ranking and Summarization:**  
  - Expands recruiter queries using OpenAI.
  - Re-ranks candidates based on semantic relevance.
  - Generates concise summaries for candidate resumes.

- **Parallel Processing:**  
  - Uses multi-processing (5 concurrent processes) for summary generation.
  
- **Logging and Output:**  
  - Detailed logs are written to a dedicated logs folder.
  - Final candidate results and summaries are exported to a unique Excel file in the output folder.

## Directory Structure

```plaintext
/asendia                   # Project root
├── database               # Contains DBManager and database files (e.g., resumes.db)
├── logs                   # Log files for application run-time logs
├── output                 # Excel output files with candidate summaries
├── prompts                # Text files containing prompts for LLM tasks
├── resumes                # Source resumes (CSV)
├── utils                  # Utility modules (config, logger, text_cleaner, resume_parser, llm_client, prompt_loader, file_converter)
├── vectordb               # Vector index and precomputed filter modules (vector_index, precomputed_filter)
├── config.json            # Configuration file with API keys and other settings
├── candidate_ids.json     # Persisted mapping for candidate IDs in vector index
├── faiss.index            # Persisted FAISS vector index file
├── main.py                # Main application file
├── precomputed_filter.pkl # Cached BM25 and TF–IDF indices
└── requirements.txt       # Python package requirements
```

## Installation

1. **Clone the repository:**

   ```bash
   git clone <repository_url>
   cd asendia
   ```

2. **Create a virtual environment (recommended):**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set up Configuration:**  
   Update the `config.json` file in the project root with your OpenAI API key and any other configuration settings.

5. **Environment Variables:**  
   To suppress parallelism warnings from Hugging Face tokenizers, set the environment variable at the start of your run:
   
   ```bash
   export TOKENIZERS_PARALLELISM=false
   ```

## Usage

Run the main application script to start indexing and process a recruiter query:

```bash
python main.py
```

### What Happens:

- The application indexes resumes from the `resumes` folder (both CSV and PDF files).  
- It processes a recruiter query (e.g., "Give me top 5 Data Scientists") by:
  - Expanding the query using OpenAI.
  - Filtering resumes using BM25 and TF–IDF (precomputed or updated automatically).
  - Performing vector search on the FAISS index.
  - Re-ranking candidates using LLM-based evaluation.
  - Generating summaries for each candidate in parallel.
- Final candidate data (CandidateID, Name, AI-generated summary, Resume text) are saved into a unique Excel file in the `output` folder.
- All detailed logs are written to files in the `logs` folder (no extra output is printed on the CLI).

## Logging

The logging is configured via `utils/logger.py` to use a FileHandler only. All logs are stored in `logs/query_log.txt`. If you wish to change the logging level or output file, modify this file accordingly.

## Troubleshooting

- **Parallelism Warnings:**  
  If you see warnings from Hugging Face's tokenizers regarding forked processes, ensure you have set `TOKENIZERS_PARALLELISM=false` in your environment.
  
- **Index Updates:**  
  The system automatically caches BM25 and TF–IDF indices in `precomputed_filter.pkl`. If new resumes are added, the cached indices will be re-computed automatically.

## Contributing

Contributions are welcome! Please follow best practices and update tests/documentation as necessary.

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

---

This **README.md** provides a clear overview of the project, installation instructions, usage guidelines, and troubleshooting steps to help users get started with the Asendia Resume Matching System.