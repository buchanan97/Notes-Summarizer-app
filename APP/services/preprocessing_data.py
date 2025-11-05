#alright guys here is where servoces/prepocessing data starts
#importing nltk and creating the class for preprocessing data

import nltk
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS

#class for preprocessing data, using inheritance
class PreprocessingData:
    def __init__(self):
        nltk.download('punkt')
        nltk.download('wordies')
        self.lemmatizer = nltk.WordNetLemmatizer()

    def clean_text(self, text):
        tokens = nltk.word_tokenize(text.lower())
        tokens = [self.lemmatizer.lemmatize(tok) for tok in tokens if tok.isalpha() and tok not in ENGLISH_STOP_WORDS]
        return ' '.join(tokens)
    