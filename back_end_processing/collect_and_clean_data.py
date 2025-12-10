import os
import sys
from PyPDF2 import PdfReader
import re

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
if project_root not in sys.path:
    sys.path.append(project_root)

from APP.services.preprocessing_data import Preprocessor

RAW_DIR = os.path.join(project_root, "data", "raw_notes")
PROCESSED_DIR = os.path.join(project_root, "data", "processed_data")

processor = Preprocessor()


def clean_pdf_extraction(text):

    text = re.sub(r'(\w+)-\s*\n\s*(\w+)', r'\1\2', text)

    text = re.sub(r'(\w)\s*\n\s*(\w)', r'\1 \2', text)
    
    text = re.sub(r'(?<=[a-z0-9])(?=[A-Z])', ' ', text)

    text = re.sub(r'\s+', ' ', text)

    text = re.sub(r'(?:\.\s*){3,}', ' ', text)

    text = re.sub(r'(?:\.\s*){3,}', ' ', text)      

    text = re.sub(r'^\s*\d+\s*$', '', text, flags=re.MULTILINE)

    return text.strip()


def convert_pdf_to_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""

    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"

    text = re.sub(r"(\w+)-\s*\n\s*(\w+)", r"\1\2", text)
    
    clean_text = clean_pdf_extraction(text)

    if len(clean_text) > 60000:
        clean_text = clean_text[:60000]

    return clean_text

def collect_and_clean():
    print(f"Starting data collection and cleaning...")
    print(f"Reading raw notes from: {RAW_DIR}")
    print(f"Writing processed data to: {PROCESSED_DIR}")

    os.makedirs(PROCESSED_DIR, exist_ok=True)

    for root, dirs, files in os.walk(RAW_DIR):
        rel_path = os.path.relpath(root, RAW_DIR)
        if rel_path == ".":
            continue

        source_folder = rel_path.split(os.sep)[0]
        out_dir = os.path.join(PROCESSED_DIR, source_folder)
        os.makedirs(out_dir, exist_ok=True)

        for file in files:
            file_path = os.path.join(root, file)
            text = ""

            if file.lower().endswith(".pdf"):
                print(f"  Converting PDF: {file} ({source_folder})")
                try:
                    text = convert_pdf_to_text(file_path)
                except Exception as e:
                    print(f"  ERROR processing PDF '{file}': {e}")
                    continue

            elif file.lower().endswith(".txt"):
                print(f"  Reading TXT: {file} ({source_folder})")
                try:
                    with open(file_path, "r", encoding="utf-8") as f:
                        text = f.read()
                except Exception as e:
                    print(f"  ERROR reading TXT '{file}': {e}")
                    continue

            else:
                print(f"  Skipping unsupported file: {file}")
                continue

            if not text or len(text.strip()) == 0:
                print(f"  WARNING: Empty extract for {file}")
                continue

            clean_text = processor.clean_text(text)

            lower_path = file_path.lower()

            if "reading_materials" in lower_path or "materials" in lower_path:
                source_label = "B.Tech CS Materials"
            elif "mit_opencourseware" in lower_path or "mit" in lower_path:
                source_label = "MIT OpenCourseWare"
            elif "openstax" in lower_path:
                source_label = "OpenStax"
            elif "opentextbooklibrary" in lower_path or "opentextbook" in lower_path:
                source_label = "Open Textbook Library"
            else:
                source_label = "General Resource"

            clean_text = f"[SOURCE: {source_label}] {clean_text}"

            words = clean_text.split()
            chunk_size = 280
            chunks = [
                " ".join(words[i:i + chunk_size])
                for i in range(0, len(words), chunk_size)
            ]

            base_name = file.replace(".pdf", "").replace(".txt", "")

            for idx, chunk in enumerate(chunks):
                out_filename = (
                    f"{base_name}.txt" if idx == 0 else f"{base_name}_{idx}.txt"
                )
                out_path = os.path.join(out_dir, out_filename)

                try:
                    with open(out_path, "w", encoding="utf-8") as f:
                        f.write(chunk)
                    print(f"  Processed → {source_folder}/{out_filename}")
                except Exception as e:
                    print(f"  ERROR writing file '{out_filename}': {e}")

    print("Data collection and cleaning finished.")

if __name__ == "__main__":
    collect_and_clean()
