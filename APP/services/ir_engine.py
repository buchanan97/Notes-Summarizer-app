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
    def __init__(self, processed_data_folder): # Rename parameter to reflect content
        self.processed_data_folder = processed_data_folder

        self.inverted_index_file = os.path.join(self.processed_data_folder, 'inverted_index.json')
        self.doc_vectors_file = os.path.join(self.processed_data_folder, 'doc_vectors.json') # Renamed from tfidf_vectorizer.pkl/py for clarity

        self.stopwords = set(stopwords.words("english"))
        self.lemmatizer = WordNetLemmatizer()
        self.stemmer = PorterStemmer()

        self.docs = [] # Will store text content of processed documents
        self.doc_filenames = [] # Will store original filenames (e.g., "lecture1.txt")
        self.N = 0 # Number of documents

        self.inverted_index = defaultdict(list)
        self.doc_lengths = {}
        self.doc_vectors = {}

        self._initialize_ir_assets() # New method to handle loading/building

    def _initialize_ir_assets(self):
        """
        Loads processed documents (TXT files) and then either loads pre-built
        IR assets (inverted index, TF-IDF vectors) or builds and saves them.
        """
        # Step 1: Always load the processed text documents first
        self.docs, self.doc_filenames = self._load_processed_documents()
        self.N = len(self.docs)

        if not self.docs:
            print(f"WARNING: No processed documents found in {self.processed_data_folder}. IR engine will be empty.")
            return # Cannot build index if no documents

        # Step 2: Try to load existing IR assets
        if os.path.exists(self.inverted_index_file) and os.path.exists(self.doc_vectors_file):
            print("Loading existing inverted index and TF-IDF vectors...")
            self._load_index_and_vectors()
        else:
            print("Building inverted index and TF-IDF vectors from scratch...")
            self.build_index()
            self.build_tfidf_vectors()
            self._save_index_and_vectors() # Save them after building

    def _load_processed_documents(self):
        """
        Reads the cleaned .txt files from the processed_data_folder.
        """
        all_docs_text = []
        all_doc_filenames = []
        # Ensure the directory exists
        if not os.path.exists(self.processed_data_folder):
            print(f"Error: Processed data folder '{self.processed_data_folder}' not found.")
            return [], [] # Return empty lists

        for file in os.listdir(self.processed_data_folder):
            if file.lower().endswith(".txt"):
                path = os.path.join(self.processed_data_folder, file)
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        all_docs_text.append(f.read())
                        all_doc_filenames.append(file) # Store the actual filename
                except Exception as e:
                    print(f"Error reading processed file {file}: {e}")
        return all_docs_text, all_doc_filenames
    
    def get_document_text(self, filename):
        """
        Retrieves the full text content of a document given its filename.
        Assumes documents are stored in self.processed_data_path.
        """
        doc_path = os.path.join(self.processed_data_folder, filename)
        try:
            with open(doc_path, 'r', encoding='utf-8') as f:
                return f.read()
        except FileNotFoundError:
            print(f"ERROR: Document file not found: {doc_path}")
            return None
        except Exception as e:
            print(f"ERROR: Could not read document {filename}: {e}")
            return None

    def _save_index_and_vectors(self):
        """Saves the inverted index and TF-IDF vectors to JSON files."""
        try:
            # Save inverted index
            with open(self.inverted_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.inverted_index, f)

            # Save TF-IDF vectors (convert int keys to string for JSON)
            serializable_doc_vectors = {str(k): v for k, v in self.doc_vectors.items()}
            with open(self.doc_vectors_file, 'w', encoding='utf-8') as f:
                json.dump(serializable_doc_vectors, f)
            print("IR assets (inverted index, doc vectors) saved successfully.")
        except Exception as e:
            print(f"Error saving IR assets: {e}")

    def _load_index_and_vectors(self):
        """Loads the inverted index and TF-IDF vectors from JSON files."""
        try:
            # Load inverted index
            with open(self.inverted_index_file, 'r', encoding='utf-8') as f:
                self.inverted_index = defaultdict(list, json.load(f))

            # Load TF-IDF vectors (convert string keys back to int)
            with open(self.doc_vectors_file, 'r', encoding='utf-8') as f:
                loaded_vectors = json.load(f)
                self.doc_vectors = {int(k): v for k, v in loaded_vectors.items()}
            print("IR assets (inverted index, doc vectors) loaded successfully.")
        except Exception as e:
            print(f"Error loading IR assets: {e}. Rebuilding will occur.")
            # If loading fails, force a rebuild on next start
            self.inverted_index = defaultdict(list)
            self.doc_vectors = {}

    def preprocess(self, text):
        """
        Standard preprocessing: lowercase, tokenize, remove non-alphanumeric,
        remove stopwords, lemmatize, and stem.
        """
        text = text.lower()
        tokens = word_tokenize(text)

        cleaned = []
        for tok in tokens:
            tok = re.sub(r"[^a-z0-9]", "", tok) # Remove anything not a-z or 0-9
            if not tok: # Skip empty tokens
                continue
            if tok in self.stopwords:
                continue

            tok = self.lemmatizer.lemmatize(tok)
            tok = self.stemmer.stem(tok)

            cleaned.append(tok)

        return cleaned

    def build_index(self):
        """Builds the inverted index from the processed documents."""
        self.inverted_index = defaultdict(list) # Reset in case of rebuild
        self.doc_lengths = {}

        for doc_id, text in enumerate(self.docs):
            tokens = self.preprocess(text)

            tf = defaultdict(int)
            for tok in tokens:
                tf[tok] += 1

            self.doc_lengths[doc_id] = len(tokens)

            for tok, freq in tf.items():
                self.inverted_index[tok].append((doc_id, freq))
        print("Inverted index built.")


    def compute_idf(self, term):
        """Computes Inverse Document Frequency for a given term."""
        df = len(self.inverted_index.get(term, []))
        if df == 0:
            return 0
        return math.log(self.N / df) # Using N from self.docs, which are pre-loaded

    def build_tfidf_vectors(self):
        """Builds TF-IDF vectors for all documents."""
        self.doc_vectors = {} # Reset in case of rebuild

        term_idfs = {term: self.compute_idf(term) for term in self.inverted_index}

        for doc_id in range(self.N):
            vec = {}
            doc_terms_and_freqs = defaultdict(int)
            for term, postings in self.inverted_index.items():
                for p_doc_id, freq in postings:
                    if p_doc_id == doc_id:
                        doc_terms_and_freqs[term] = freq

            # Calculate TF-IDF for terms in this document
            for term, freq in doc_terms_and_freqs.items():
                idf = term_idfs.get(term, 0) # Use pre-computed IDF
                vec[term] = freq * idf

            # Normalize the vector (L2 normalization)
            length = math.sqrt(sum(v * v for v in vec.values()))
            if length > 0:
                vec = {t: v / length for t, v in vec.items()}
            else: # Handle empty vectors
                vec = {}

            self.doc_vectors[doc_id] = vec
        print("TF-IDF vectors built.")


    def cosine_sim(self, v1, v2):
        """Computes cosine similarity between two vectors."""
        score = 0
        for term in v1:
            if term in v2:
                score += v1[term] * v2[term]
        return score

    def search(self, query):
        """Performs a search for the given query and returns top relevant documents."""
        query_tokens = self.preprocess(query)

        if not query_tokens:
            return [] # No tokens to search for

        # Calculate TF for query
        q_tf = defaultdict(int)
        for tok in query_tokens:
            q_tf[tok] += 1

        # Calculate TF-IDF vector for query
        q_vec = {}
        for tok, freq in q_tf.items():
            idf = self.compute_idf(tok)
            q_vec[tok] = freq * idf

        length = math.sqrt(sum(v * v for v in q_vec.values()))
        if length > 0:
            q_vec = {t: v / length for t, v in q_vec.items()}
        else:
            return [] 

        scored = []
        for doc_id in range(self.N):
            sim = self.cosine_sim(q_vec, self.doc_vectors.get(doc_id, {})) 
            scored.append((doc_id, sim))

        scored.sort(key=lambda x: x[1], reverse=True)

        results = []
        for doc_id, score in scored:
            if score > 0: 
                para = self.get_best_paragraph(self.docs[doc_id], query_tokens)
                results.append({
                    "doc_id": doc_id,
                    "score": float(score),
                    "paragraph": para,
                    "filename": self.doc_filenames[doc_id] 
                })
        return results[:5] 


    def get_best_paragraph(self, text, query_tokens): 
        paragraphs = re.split(r"\n\s*\n", text) 

        best_score = -1 
        best_para_full = "" 

        if not paragraphs:
            return ""

        for p in paragraphs:
            if not p.strip(): 
                continue
            tokens = self.preprocess(p)
            score = sum(1 for t in tokens if t in query_tokens) 

            if score > best_score:
                best_score = score
                best_para_full = p.strip()
                
        return best_para_full or (paragraphs[0].strip() if paragraphs else "")


        