import re
import nltk
from nltk.tokenize import sent_tokenize
from sklearn.feature_extraction.text import TfidfVectorizer

nltk.download('punkt', quiet=True)

class Summarizer:

    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')

    def clean_text(self, text):
        text = re.sub(r"\.{3,}", " ", text)
        text = re.sub(r"\s+", " ", text)
        return text.strip()

    def extract_sentences(self, text):
        if not text:
            return []

        text = re.sub(r"\[SOURCE:.*?\]", "", text)

        text = re.sub(r"(\w)-\s*\n\s*(\w)", r"\1\2", text)

        text = re.sub(r"\n{2,}", "\n", text)     
        
        text = re.sub(r"(?<!\.)\n(?!\n)", " ", text)

        text = re.sub(r"(?<=\w)(?=[A-Z])", " ", text)

        text = re.sub(r"\s{2,}", " ", text).strip()

        try:
            sentences = sent_tokenize(text)
        except:
            nltk.download("punkt")
            sentences = sent_tokenize(text)

        clean_sentences = []
        for s in sentences:
            s2 = s.strip()

            if len(s2.split()) < 4:
                continue

            if re.match(r"^[A-Z ]{1,20}$", s2):
                continue
            
            clean_sentences.append(s2)

        return clean_sentences

    def score_sentences(self, sentences, query):
        if not sentences:
            return []

        corpus = [query] + sentences
        tfidf = self.vectorizer.fit_transform(corpus)
        query_vec = tfidf[0]
        sent_vecs = tfidf[1:]

        scores = (sent_vecs * query_vec.T).toarray().flatten()
        return scores

    def summarize(self, paragraph, query, max_sentences=3):
        paragraph = self.clean_text(paragraph)
        sentences = self.extract_sentences(paragraph)

        if not sentences:
            return paragraph[:250] + "..."

        scores = self.score_sentences(sentences, query)
        ranked = sorted(zip(sentences, scores), key=lambda x: x[1], reverse=True)

        best_sentences = [s for s, _ in ranked[:max_sentences]]
        summary = " ".join(best_sentences)
        return summary.strip()
