import re

class Preprocessor:
    def __init__(self):
        pass

    def clean_text(self, text):
        if not text:
            return ""
        
        text = re.sub(r'(\w)-\s*\n\s*(\w)', r'\1\2', text)
        text = text.replace("\n", " ")
        text = re.sub(r"\.{3,}", " ", text)
        text = re.sub(r"\b\d+\.\d+(?:\.\d+)*\b", " ", text)
        text = re.sub(r"\b\d{1,3}\b", " ", text)
        text = re.sub(r"[^a-zA-Z0-9,.!?;:()\"' \-]", " ", text)
        text = re.sub(r'(?<=\w)\s+(?=\w)', ' ', text)
        text = re.sub(r"\s{2,}", " ", text)

        return text.strip()
    
    def clean_for_index(self, text):
        if not text:
            return ""

        text = text.lower()
        text = re.sub(r"\s{2,}", " ", text)

        return text.strip()
