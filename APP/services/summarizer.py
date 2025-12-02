# APP/services/summarizer.py

# --- Necessary imports for sumy library ---
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.utils import get_stop_words # This is crucial for stop words

import nltk # Only nltk is needed directly here, not other specific NLTK modules like word_tokenize etc.

class Summarizer:
    def __init__(self):
       # Ensure NLTK 'punkt' tokenizer data is available.
       # It's best practice to run 'python3 -m nltk.downloader punkt' once manually.
       try:
           nltk.data.find('tokenizers/punkt')
       except LookupError:
              # If not found, explicitly tell the user to download it.
              # REMOVE 'nltk.download('punkt')' here to avoid repeated downloads and potential issues.
              raise Exception(
                  "NLTK 'punkt' tokenizer data not found. "
                  "Please run 'python3 -m nltk.downloader punkt' in your virtual environment."
              )

       self.summarizer = LexRankSummarizer()
       self.summarizer.stop_words = get_stop_words("english")

    def summarize_text(self, text, sentence_count=3):
        """
        Summarizes the input text using the LexRank algorithm.
        Includes validation checks and handles potential errors.
        """
        # --- Validation checks for text based on input from user ---
        if not text or not isinstance(text, str):
            return "No text provided for summarization."   
    
        # --- Normalizing whitespace before processing ---
        # Replace multiple spaces, newlines, tabs with a single space to clean text
        text = " ".join(text.split())

        if len(text) < 50: # Text should be reasonably long for summarization
            return "Text too short to summarize."
        
        # Limit input text length for performance/resource reasons if very large documents
        # For example, sumy might struggle with extremely long inputs
        if len(text) > 100000: # limit to 100,000 characters
             text = text[:100000]
             print("[WARNING] Summarizer: Input text truncated due to excessive length.")

        try:
            # --- Parsing through raw text data, to identify sentence boundaries ---
            # Tokenizer needs to be initialized with the language
            parser = PlaintextParser.from_string(text, Tokenizer("english"))

            # --- Generate summary using LexRank algorithm and joining the sentences as object back into the string ---
            summary_sentences = self.summarizer(parser.document, sentence_count)
            summarized_text = " ".join([str(sentence) for sentence in summary_sentences])
        
            if not summarized_text:
                return "Summarization failed, generated an empty summary. Please try again."
            return summarized_text

        except Exception as e:
            # Catch broader exceptions during summarization
            return f"Summarization failed: An unexpected error occurred: {str(e)}"

    def summarize(self, text, sentence_count=3):
        """
        Public method to call the internal summarization logic.
        """
        return self.summarize_text(text, sentence_count)