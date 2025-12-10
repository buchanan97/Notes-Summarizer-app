import nltk
import math
import re
import os
import json

from nltk.tokenize import word_tokenize
from nltk.stem import WordNetLemmatizer, PorterStemmer
from nltk.corpus import stopwords
from collections import defaultdict


class IREngine:
    def __init__(self, processed_data_folder):
        self.processed_data_folder = processed_data_folder

        self.inverted_index_file = os.path.join(self.processed_data_folder, 'inverted_index.json')
        self.doc_vectors_file = os.path.join(self.processed_data_folder, 'doc_vectors.json')

        self.stopwords = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()

        self.docs = []
        self.doc_filenames = []
        self.N = 0

        self.inverted_index = defaultdict(list)
        self.doc_lengths = {}
        self.doc_vectors = {}

        self._initialize_ir_assets()

    def _initialize_ir_assets(self):
        self.docs, self.doc_filenames = self._load_processed_documents()
        self.N = len(self.docs)

        if not self.docs:
            print(f"WARNING: No processed documents in {self.processed_data_folder}")
            return

        if os.path.exists(self.inverted_index_file) and os.path.exists(self.doc_vectors_file):
            self._load_index_and_vectors()
            print("IR assets loaded successfully.")
        else:
            print("Building IR assets from scratch…")
            self.build_index()
            self.build_tfidf_vectors()
            self._save_index_and_vectors()

    def _load_processed_documents(self):
        all_text = []
        all_filenames = []

        for root, dirs, files in os.walk(self.processed_data_folder):
            for file in files:
                if file.lower().endswith(".txt"):
                    path = os.path.join(root, file)
                    try:
                        with open(path, "r", encoding="utf-8") as f:
                            all_text.append(f.read())
                            all_filenames.append(path)
                        #print(f"DEBUG: Loaded processed file {path}")
                    except Exception as e:
                        print(f"Error reading processed file {file}: {e}")

        return all_text, all_filenames

    def _save_index_and_vectors(self):
        try:
            with open(self.inverted_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.inverted_index, f)

            serializable_vectors = {str(k): v for k, v in self.doc_vectors.items()}
            with open(self.doc_vectors_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_vectors, f)
            print("IR assets saved successfully.")
        except Exception as e:
            print(f"Saving IR assets failed: {e}")

    def _load_index_and_vectors(self):
        try:
            with open(self.inverted_index_file, 'r', encoding='utf-8') as f:
                self.inverted_index = defaultdict(list, json.load(f))

            with open(self.doc_vectors_file, 'r', encoding='utf-8') as f:
                vecs = json.load(f)
                self.doc_vectors = {int(k): v for k, v in vecs.items()}
        except Exception as e:
            print(f"Error loading IR assets, rebuilding required: {e}")
            self.inverted_index = defaultdict(list)
            self.doc_vectors = {}

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
        self.inverted_index = defaultdict(list)
        self.doc_lengths = {}

        for doc_id, text in enumerate(self.docs):
            tokens = self.preprocess(text)

            tf = defaultdict(int)
            for t in tokens:
                tf[t] += 1

            self.doc_lengths[doc_id] = len(tokens)

            for term, freq in tf.items():
                self.inverted_index[term].append((doc_id, freq))

        print("Inverted index built.")

    def compute_idf(self, term):
        df = len(self.inverted_index.get(term, []))
        if df == 0:
            return 0
        return math.log(self.N / df)

    def build_tfidf_vectors(self):
        self.doc_vectors = {}

        idf_cache = {t: self.compute_idf(t) for t in self.inverted_index}

        for doc_id in range(self.N):
            vec = {}
            term_freqs = defaultdict(int)

            for term, postings in self.inverted_index.items():
                for p_doc, freq in postings:
                    if p_doc == doc_id:
                        term_freqs[term] = freq

            for term, freq in term_freqs.items():
                vec[term] = freq * idf_cache.get(term, 0)

            length = math.sqrt(sum(v * v for v in vec.values()))
            if length > 0:
                vec = {t: v / length for t, v in vec.items()}

            self.doc_vectors[doc_id] = vec

        print("TF-IDF vectors built.")

    def clean_paragraph(self, text):
        text = re.sub(r'\.{5,}', ' ', text)
        text = re.sub(r'\b\d+\b', '', text)
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def get_best_paragraph(self, full_text, query_tokens):
        paragraphs = re.split(r"\n\s*\n", full_text)
        best_score = -1
        best_para = ""

        query_set = set(query_tokens)

        for p in paragraphs:
            p = self.clean_paragraph(p)
            if not p:
                continue

            tokens = self.preprocess(p)
            if not tokens:
                continue

            tf = defaultdict(int)
            for t in tokens:
                tf[t] += 1

            score = 0
            for t in query_set:
                if t in tf:
                    score += tf[t] * self.compute_idf(t)

            if score > best_score:
                best_score = score
                best_para = p

        return best_para

    def cosine_sim(self, v1, v2):
        return sum(v1.get(t, 0) * v2.get(t, 0) for t in v1)

    def search(self, query):
        q_tokens = self.preprocess(query)
        if not q_tokens:
            return []

        q_tf = defaultdict(int)
        for t in q_tokens:
            q_tf[t] += 1

        q_vec = {}
        for t, freq in q_tf.items():
            q_vec[t] = freq * self.compute_idf(t)

        q_len = math.sqrt(sum(v * v for v in q_vec.values()))
        if q_len > 0:
            q_vec = {t: v / q_len for t, v in q_vec.items()}

        scores = []
        for doc_id in range(self.N):
            sim = self.cosine_sim(q_vec, self.doc_vectors.get(doc_id, {}))
            scores.append((doc_id, sim))

        scores.sort(key=lambda x: x[1], reverse=True)

        TOP_K = 50

        results = []
        for doc_id, score in scores[:TOP_K]:
            paragraph = self.get_best_paragraph(self.docs[doc_id], q_tokens)
            filename = self.doc_filenames[doc_id]

            results.append({
                "doc_id": doc_id,
                "score": float(score),
                "paragraph": paragraph,
                "filename": filename
            })

        return results
