import os
from PyPDF2 import PdfReader
from APP.services.preprocessing_data import PreprocessingData

RAW_DIR = "APP/data/raw_notes"
PROCESSED_DIR = "APP/data/processed_data"

processor = PreprocessingData()

def convert_pdf_to_text(pdf_path):
    reader = PdfReader(pdf_path)
    text = ""
    for page in reader.pages:
        extracted = page.extract_text()
        if extracted:
            text += extracted + "\n"
    if len(text) > 30000:
        text = text[:30000]
    return text

def collect_and_clean():
    if not os.path.exists(PROCESSED_DIR):
        os.makedirs(PROCESSED_DIR)

    for file in os.listdir(RAW_DIR):
        file_path = os.path.join(RAW_DIR, file)

        if file.endswith(".pdf"):
            text = convert_pdf_to_text(file_path)
        elif file.endswith(".txt"):
            with open(file_path, "r", encoding="utf-8") as f:
                text = f.read()
        else:
            print(f"Skipping unsupported file: {file}")
            continue

        clean_text = processor.clean_text(text)

        out_file = os.path.join(PROCESSED_DIR, file.replace(".pdf", ".txt"))
        with open(out_file, "w", encoding="utf-8") as f:
            f.write(clean_text)
        print("Processed: {file} → {out_file}")

if __name__ == "__main__":
    collect_and_clean()
