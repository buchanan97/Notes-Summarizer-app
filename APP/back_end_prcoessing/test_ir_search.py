from APP.services.ir_engine import IREngine
import os

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

queries = [
    "machine learning",
    "computer networks",
    "data structures"
]

for q in queries:
    print(f"Query: {q}")
    results = ir.query(q)
    for doc, score in results:
        print(f"  → {filenames[docs.index(doc)]} (score: {score:.4f})")
