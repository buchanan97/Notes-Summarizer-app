# notes-summarizer-app/back_end_processing/test_ir_summary.py
import os
import sys

# --- Add the project root to sys.path ---
# This script is in 'notes-summarizer-app/back_end_processing/'
# So, the project_root is one level up from this script's directory.
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Import the IREngine and Summarizer services
from APP.services.ir_engine import IREngine
from APP.services.summarizer import Summarizer # Assuming class is now named Summarizer

# Define the path to the processed data directory
PROCESSED_DATA_DIR = os.path.join(project_root, "data", "processed_data")

def run_ir_summary_tests():
    print(f"--- Running IR & Summary Tests ---")
    print(f"Initializing IREngine with processed data from: {PROCESSED_DATA_DIR}")

    try:
        ir_engine = IREngine(PROCESSED_DATA_DIR)
        summarizer = Summarizer() # Instantiate the Summarizer

        if not ir_engine.docs:
            print("WARNING: IREngine has no documents loaded. Ensure 'collect_and_clean_data.py' has been run.")
            return

        queries = [
            "machine learning introduction",
            "database management systems",
            "operating system concepts",
        ]

        for q in queries:
            print(f"\nQuery: '{q}'")
            results = ir_engine.search(q) # Use .search method

            if not results:
                print("  No relevant documents found for this query.")
                continue

            # Get the top document from the results
            top_result = results[0]
            top_doc_id = top_result['doc_id']
            top_filename = top_result.get('filename', f"Document {top_doc_id}")
            top_score = top_result.get('score', 0.0)
            top_paragraph = top_result.get('paragraph', 'No relevant paragraph found.')

            print(f"  Top match: {top_filename} (score: {top_score:.4f})")
            print(f"  Snippet from top document: {top_paragraph[:200]}...") # Show a longer snippet

            print("\n  Summary of top relevant paragraph:")
            try:
                # Summarize the relevant paragraph from the top document
                summary_text = summarizer.summarize(top_paragraph, sentence_count=3)
                print(f"    {summary_text}")
            except Exception as e:
                print(f"    Error summarizing paragraph: {e}")
                
            # Optionally, summarize the entire document
            # print("\n  Summary of entire top document:")
            # try:
            #     full_doc_text = ir_engine.get_document_by_id(top_doc_id)['text']
            #     full_summary = summarizer.summarize(full_doc_text, sentence_count=5)
            #     print(f"    {full_summary}")
            # except Exception as e:
            #     print(f"    Error summarizing full document: {e}")


    except Exception as e:
        print(f"An error occurred during IR and Summary tests: {e}")

if __name__ == "__main__":
    run_ir_summary_tests()