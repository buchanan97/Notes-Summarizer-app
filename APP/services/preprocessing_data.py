import re

class Preprocessor:
    def __init__(self):
        pass

    def clean_text(self, text):
        """"
        Cleans the input summarization/display purposes.
        Preserves punctuation, case, and stopwords to ensure 
        the summarizer can detect sentence boundaries.
        """
        if not text:
            return "" 
        text = " ".join(text.split()) 

        return text.strip() 
