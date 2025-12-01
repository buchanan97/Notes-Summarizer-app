# notes-summarizer-app/back_end_processing/collect_and_clean_data.py
import os
import sys
from PyPDF2 import PdfReader
import re

# --- Add the project root to sys.path BEFORE any other imports that rely on it ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

# Now, import your preprocessor from APP.services
from APP.services.preprocessing_data import Preprocessor

# Correct RAW_DIR and PROCESSED_DIR using the project_root
RAW_DIR = os.path.join(project_root, "data", "raw_notes")
PROCESSED_DIR = os.path.join(project_root, "data", "processed_data")

# Instantiate the preprocessor with the correct class name
processor = Preprocessor()

def convert_pdf_to_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    
    # PDF cleanup logic
    text = re.sub(r'^\s*-?\s*\d+\s*-?\s*$', '', text, flags=re.MULTILINE)
    text = re.sub(r'(\w+)-\n(\w+)', r'\1\2', text)
    lines = text.split('\n')
    cleaned_lines = []
    for line in lines:
        if len(line.strip()) < 4 and not re.match(r'[A-Za-z0-9]+$', line.strip()):
            continue
        cleaned_lines.append(line)
    text = "\n".join(cleaned_lines)

    if len(text) > 30000:
        text = text[:30000]
    return text

# THIS IS THE *ONLY* collect_and_clean function that should be in the file
def collect_and_clean():
    print(f"Starting data collection and cleaning...")
    print(f"Reading raw notes from: {RAW_DIR}")
    print(f"Writing processed data to: {PROCESSED_DIR}")

    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)

    for file in os.listdir(RAW_DIR):
        file_path = os.path.join(RAW_DIR, file)
        
        # Skip directories
        if os.path.isdir(file_path):
            continue

        text = ""
        if file.lower().endswith(".pdf"):
            print(f"  Converting PDF: {file}")
            try: # <--- THIS IS THE TRY BLOCK
                text = convert_pdf_to_text(file_path)
            except Exception as e: # <--- THIS IS THE EXCEPT BLOCK
                print(f"  ERROR: Failed to process PDF '{file}': {e}. Skipping this file.")
                continue # <--- SKIP TO THE NEXT FILE
        elif file.lower().endswith(".txt"):
            print(f"  Reading TXT: {file}")
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    text = f.read()
            except Exception as e:
                print(f"  Error reading {file}: {e}. Skipping.")
                continue
        else:
            print(f"  Skipping unsupported file: {file}")
            continue

        if text:
            clean_text = processor.clean_text(text)
            out_filename = file.replace(".pdf", ".txt")
            out_file_path = os.path.join(PROCESSED_DIR, out_filename)
            try:
                with open(out_file_path, "w", encoding="utf-8") as f:
                    f.write(clean_text)
                print(f"  Processed: {file} → {os.path.basename(out_file_path)}")
            except Exception as e:
                print(f"  Error writing processed file {out_filename}: {e}")
        else:
            print(f"  No content extracted/read from {file}. Skipping processing.")

    print("Data collection and cleaning finished.")

if __name__ == "__main__":
    collect_and_clean()