# services/summarizer.py

#her is the code for the summarizer service

#taking the sumy library to summarize text, and importing the library here so that the class works out. 
# please run pip install sumy if you have not already installed it. or else you will get an error
from sumy.parsers.plaintext import PlaintextParser
from sumy.nlp.tokenizers import Tokenizer
from sumy.summarizers.lsa import LsaSummarizer
from sumy.nlp.stemmers import Stemmer
from sumy.utils import get_stop_words

class summarizer:
    def summarize(self, text, ratio=0.2):
        try:
            parser = PlaintextParser.from_string(text, Tokenizer("english"))
            stemmer = Stemmer("english")
            summarizer = LsaSummarizer(stemmer)
            summarizer.stop_words = get_stop_words("english")
            
            sentence_count = max(int(len(parser.document.sentences) * ratio), 1)
            summary = [str(sent) for sent in summarizer(parser.document, sentence_count)]
            if summary:
                return " ".join(summary)
                return "Text too short to summarize"
        except ValueError as e:
            return str(e)
