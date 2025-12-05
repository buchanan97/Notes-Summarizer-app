import os
import sys

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from APP.services.ir_engine import IREngine
from APP.services.summarizer import Summarizer 

PROCESSED_DATA_DIR = os.path.join(project_root, "data", "processed_data")

def run_ir_summary_tests():
    print(f"--- Running IR & Summary Tests ---")
    print(f"Initializing IREngine with processed data from: {PROCESSED_DATA_DIR}")

    try:
        ir_engine = IREngine(PROCESSED_DATA_DIR)
        summarizer = Summarizer() 

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
            results = ir_engine.search(q) 

            if not results:
                print("  No relevant documents found for this query.")
                continue

            top_result = results[0]
            top_doc_id = top_result['doc_id']
            top_filename = top_result.get('filename', f"Document {top_doc_id}")
            top_score = top_result.get('score', 0.0)
            top_paragraph = top_result.get('paragraph', 'No relevant paragraph found.')

            print(f"  Top match: {top_filename} (score: {top_score:.4f})")
            print(f"  Snippet from top document: {top_paragraph[:200]}...") 

            print("\n  Summary of top relevant paragraph:")
            try:
                summary_text = summarizer.summarize(top_paragraph, sentence_count=3)
                print(f"    {summary_text}")
            except Exception as e:
                print(f"    Error summarizing paragraph: {e}")

    except Exception as e:
        print(f"An error occurred during IR and Summary tests: {e}")

if __name__ == "__main__":
    run_ir_summary_tests()