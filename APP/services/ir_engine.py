import nltk
import math
import re
import string
from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import stopwords
from collections import defaultdict
from PyPDF2 import PdfReader

nltk.download("punkt")
nltk.download("stopwords")
nltk.download("wordnet")

class IREngine:
    def __init__(self, pdf_folder):
        self.pdf_folder = pdf_folder
        self.docs = self.load_pdfs()
        self.N = len(self.docs)

        self.stopwords = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()

        self.inverted_index = defaultdict(list)    
        self.doc_lengths = {}                    
        self.doc_vectors = {}                     

        self.build_index()
        self.build_tfidf_vectors()

    def load_pdfs(self):
        import os
        docs = []

        for file in os.listdir(self.pdf_folder):
         if file.lower().endswith(".txt"):
            path = os.path.join(self.pdf_folder, file)
            with open(path, "r", encoding="utf-8") as f:
                text = f.read()
                docs.append(text)

        return docs


    def extract_pdf_text(self, path):
        reader = PdfReader(path)
        text = ""
        for page in reader.pages:
            extracted = page.extract_text()
            if extracted:
                text += extracted + "\n"
        return text

    def preprocess(self, text):
        text = text.lower()

        tokens = word_tokenize(text)

        cleaned = []
        for tok in tokens:
            tok = re.sub(r"[^a-z0-9]", "", tok)
            if not tok:
                continue
            if tok in self.stopwords:
                continue

            tok = self.lemmatizer.lemmatize(tok)
            tok = self.stemmer.stem(tok)

            cleaned.append(tok)

        return cleaned

    def build_index(self):
        for doc_id, text in enumerate(self.docs):
            tokens = self.preprocess(text)

            tf = defaultdict(int)
            for tok in tokens:
                tf[tok] += 1

            self.doc_lengths[doc_id] = len(tokens)

            for tok, freq in tf.items():
                self.inverted_index[tok].append((doc_id, freq))


    def compute_idf(self, term):
        df = len(self.inverted_index.get(term, []))
        if df == 0:
            return 0
        return math.log(self.N / df)

    def build_tfidf_vectors(self):
        for term in self.inverted_index:
            idf = self.compute_idf(term)

        for doc_id in range(self.N):
            vec = {}
            for term, postings in self.inverted_index.items():
                for (p_doc_id, freq) in postings:
                    if p_doc_id == doc_id:
                        vec[term] = (freq * self.compute_idf(term))

            length = math.sqrt(sum(v * v for v in vec.values()))
            if length > 0:
                vec = {t: v / length for t, v in vec.items()}

            self.doc_vectors[doc_id] = vec

    def cosine_sim(self, v1, v2):
        score = 0
        for term in v1:
            if term in v2:
                score += v1[term] * v2[term]
        return score

    def search(self, query):
        query_tokens = self.preprocess(query)

        q_tf = defaultdict(int)
        for tok in query_tokens:
            q_tf[tok] += 1

        q_vec = {}
        for tok, freq in q_tf.items():
            idf = self.compute_idf(tok)
            q_vec[tok] = freq * idf

        length = math.sqrt(sum(v * v for v in q_vec.values()))
        if length > 0:
            q_vec = {t: v / length for t, v in q_vec.items()}

        scored = []
        for doc_id in range(self.N):
            sim = self.cosine_sim(q_vec, self.doc_vectors[doc_id])
            scored.append((doc_id, sim))

        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        for doc_id, score in scored[:5]:  # top 5
            para = self.get_best_paragraph(self.docs[doc_id], query_tokens)
            results.append({
                "doc_id": doc_id,
                "score": float(score),
                "paragraph": para
            })

        return results

    def get_best_paragraph(self, text, query_tokens):
        paragraphs = re.split(r"\n\s*\n", text)

        best_score = 0
        best_para = ""

        for p in paragraphs:
            tokens = self.preprocess(p)
            score = sum(1 for t in tokens if t in query_tokens)

            if score > best_score:
                best_score = score
                best_para = p.strip()

        return best_para or paragraphs[0]
    
    def get_document_by_id(self, doc_id):
        """Return a full document for the 'Read More' view."""
        try:
            doc_id = int(doc_id)
            if 0 <= doc_id < len(self.docs):
                text = self.docs[doc_id]
                filename = f"Document {doc_id + 1}"
                return {
                    "filename": filename,
                    "text": text,
                    "summary": None  
                }
        except Exception as e:
            print(f"[ERROR] get_document_by_id failed for {doc_id}: {e}")
        return None
