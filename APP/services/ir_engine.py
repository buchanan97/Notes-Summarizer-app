from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import json

class IREngine:
    def __init__(self, docs):
        self.vectorizer = TfidfVectorizer()
        self.doc_vectors = self.vectorizer.fit_transform(docs)
        self.docs = docs

    def query(self, text):
        query_vec = self.vectorizer.transform([text])
        scores = cosine_similarity(query_vec, self.doc_vectors).flatten()
        top_indices = scores.argsort()[-3:][::-1]
        return [(self.docs[i], scores[i]) for i in top_indices]