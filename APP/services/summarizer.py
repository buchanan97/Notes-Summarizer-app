from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.utils import get_stop_words 

import nltk 

class Summarizer:
    def __init__(self):
       try:
           nltk.data.find('tokenizers/punkt')
       except LookupError:
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
        if not text or not isinstance(text, str):
            return "No text provided for summarization."   

        text = " ".join(text.split())

        if len(text) < 50: 
            return "Text too short to summarize."
        
        
        if len(text) > 100000: 
             text = text[:100000]
             print("[WARNING] Summarizer: Input text truncated due to excessive length.")

        try:
            parser = PlaintextParser.from_string(text, Tokenizer("english"))

            summary_sentences = self.summarizer(parser.document, sentence_count)
            summarized_text = " ".join([str(sentence) for sentence in summary_sentences])
        
            if not summarized_text:
                return "Summarization failed, generated an empty summary. Please try again."
            return summarized_text

        except Exception as e:
            return f"Summarization failed: An unexpected error occurred: {str(e)}"

    def summarize(self, text, sentence_count=3):
        """
        Public method to call the internal summarization logic.
        """
        return self.summarize_text(text, sentence_count)