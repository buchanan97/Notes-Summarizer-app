#alright guys here is where servoces/prepocessing data starts
#importing nltk and creating the class for preprocessing data
import re
# import nltk
# from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

# #class for preprocessing data, using inheritance
# class PreprocessingData:
#     def __init__(self):
#         nltk.download('punkt')
#         nltk.download('wordies')
#         self.lemmatizer = nltk.WordNetLemmatizer()

#     def clean_text(self, text):
#         tokens = nltk.word_tokenize(text.lower())
#         tokens = [self.lemmatizer.lemmatize(tok) for tok in tokens if tok.isalpha() and tok not in ENGLISH_STOP_WORDS]
#         return ' '.join(tokens)

#the above code is commented out since the orginal code had issues
#with removing stopwords and punctuation, so here is revised code.
#That doesn't use nltk for stopwords and punctuation removal.
# the algorithm fails to identify sentence boundaries, resulting in the output making no sense at all.
#instead I used a simpler appraoch.
#to text preprocessing using re essentially a sophisticated pattern-matching tool

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
            return "" # Return empty string for None or empty input
        
        #converting new lines/tabs to single spaces
        #believe this will help in better sentence segmentation, and if pdfs have weird spacing when extracted.
        text = " ".join(text.split()) # Replace multiple spaces/newlines/tabs with single space

        return text.strip() # Remove leading/trailing whitespace
