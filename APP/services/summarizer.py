# services/summarizer.py

#her is the code for the summarizer service

#taking the sumy library to summarize text, and importing the library here so that the class works out. 
# please run pip install sumy if you have not already installed it. or else you will get an error
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lex_rank import LexRankSummarizer
from sumy.utils import get_stop_words

class summarizer:
    def __init__(self):
        self.summarizer = LexRankSummarizer()
        self.summarizer.stop_words = get_stop_words("english")

    def summarize_text(self, text, sentence_count=3):
        text = text.strip()
        if not text or len(text.strip()) < 50:
            return "Text too short to summarize."

        if len(text) > 5000:
            text = text[:5000]

        text = " ".join(text.split())

        try:
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            summary = self.summarizer(parser.document, sentence_count)
            summarized_text = " ".join([str(sentence) for sentence in summary])
            return summarized_text or "Summarization failed."
        except Exception as e:
            return f"Summarization failed: {str(e)}"
    
    def summarize(self, text, sentence_count=3):
        return self.summarize_text(text, sentence_count)
