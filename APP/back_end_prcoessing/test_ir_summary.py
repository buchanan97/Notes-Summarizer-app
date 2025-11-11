import os
from APP.services.ir_engine import IREngine
from APP.services.summarizer import summarizer

PROCESSED_DIR = "APP/data/processed_data"

docs = []
filenames = []

for file in os.listdir(PROCESSED_DIR):
    if file.endswith(".txt"):
        path = os.path.join(PROCESSED_DIR, file)
        with open(path, "r", encoding="utf-8") as f:
            text = f.read()
            docs.append(text)
            filenames.append(file)

ir = IREngine(docs)

sumr = summarizer()

queries = [
    "machine learning",
    "computer networks",
    "information systems",
]

for q in queries:
    print(f"Query: {q}")
    results = ir.query(q)

    if not results:
        print("No relevant documents found.")
        continue

    top_doc, score = results[0]
    top_filename = filenames[docs.index(top_doc)]
    print(f"Top match: {top_filename} (score: {score:.4f})")

    print("Summary of top document:")
    try:
        summary_text = sumr.summarize(top_doc, ratio=0.1)  # Summarize 10% of sentences
        print(summary_text)
    except Exception as e:
        print("Error summarizing document:", e)
