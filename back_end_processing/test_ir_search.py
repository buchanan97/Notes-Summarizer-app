# notes-summarizer-app/back_end_processing/test_ir_search.py
import os
import sys

# --- Add the project root to sys.path ---
# This script is in 'notes-summarizer-app/back_end_processing/'
# So, the project_root is one level up from this script's directory.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the IREngine service
from APP.services.ir_engine import IREngine

# Define the path to the processed data directory
# This is where IREngine will find its .txt files and saved index/vectors
PROCESSED_DATA_DIR = os.path.join(project_root, "data", "processed_data")

def run_ir_search_tests():
    print(f"--- Running IR Search Tests ---")
    print(f"Initializing IREngine with processed data from: {PROCESSED_DATA_DIR}")

    try:
        # Initialize IREngine with the processed data directory
        ir_engine = IREngine(PROCESSED_DATA_DIR)
        
        if not ir_engine.docs:
            print("WARNING: IREngine has no documents loaded. Ensure 'collect_and_clean_data.py' has been run.")
            return

        queries = [
            "machine learning algorithms",
            "computer networks protocols",
            "data structures efficiency",
            "operating systems scheduling",
            "programming language paradigms"
        ]

        for q in queries:
            print(f"\nQuery: '{q}'")
            # Use the .search method of IREngine
            results = ir_engine.search(q)

            if not results:
                print("  No relevant documents found for this query.")
                continue

            print("  Top 5 Results:")
            for r in results:
                # The 'results' from ir_engine.search are dictionaries
                # They should contain 'filename', 'score', and 'paragraph'
                filename = r.get('filename', f"Document {r['doc_id']}")
                score = r.get('score', 0.0)
                paragraph = r.get('paragraph', 'No relevant paragraph found.')

                print(f"    -> {filename} (score: {score:.4f})")
                # print(f"       Snippet: {paragraph[:100]}...") # Optionally print a snippet
                
    except Exception as e:
        print(f"An error occurred during IR search tests: {e}")

if __name__ == "__main__":
    run_ir_search_tests()