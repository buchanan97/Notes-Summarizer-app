import os
import sys
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from APP.services.ir_engine import IREngine
PROCESSED_DATA_DIR = os.path.join(project_root, "data", "processed_data")

def run_ir_search_tests():
    print(f"--- Running IR Search Tests ---")
    print(f"Initializing IREngine with processed data from: {PROCESSED_DATA_DIR}")

    try:
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
            results = ir_engine.search(q)

            if not results:
                print("  No relevant documents found for this query.")
                continue

            print("  Top 5 Results:")
            for r in results:
                filename = r.get('filename', f"Document {r['doc_id']}")
                score = r.get('score', 0.0)
                paragraph = r.get('paragraph', 'No relevant paragraph found.')

                print(f"    -> {filename} (score: {score:.4f})")
                
    except Exception as e:
        print(f"An error occurred during IR search tests: {e}")

if __name__ == "__main__":
    run_ir_search_tests()