# Notes-Summarizer-app
Here is a link to the powerpoint and video demo https://docs.google.com/presentation/d/1l0lH19gLbbKQtOhHbgiYkUl_9B7De3yTLywjJ-7Tm1E/edit?usp=drivesdk

Mazin Alalawi, Chelsea Rivera and I will be working on a summarization AI tool. This will help anyone get a summary of what they are asking pertaining to the computer science topic they may want summarized, based on a document, article, PDF, etc.

# **📚 Intelligent Notes Summarizer & Search Engine**

This repository contains a Flask-based web application that serves as a powerful search and summarization platform for academic and professional documents. Using advanced Information Retrieval (IR) techniques and NLP, it allows users to navigate large collections of reading materials, textbooks, and notes with ease.

---

## **⚡ What This App Does**

- **Semantic Search:** Uses an Inverted Index and Vector Space Modeling to find the most relevant documents based on your queries.
- **Smart Summarization:** Automatically generates concise summaries of long text files to save reading time.
- **User Management:** Secure signup and login system with persistent history to track your recent searches.
- **Vast Knowledge Base:** Built to handle diverse data sources, including MIT OpenCourseWare, OpenStax, and Open Textbook Library.
- **High Performance:** Backend processing pre-calculates document vectors for near-instant search results.

---

## **📁 Repository Structure**

| File / Folder | Description |
| :--- | :--- |
| `app.py` | The main entry point of the Flask application. |
| `routes.py` | Handles all URL routing for authentication, searching, and viewing results. |
| `APP/services/` | **Core Logic:** Contains `ir_engine.py` (Search logic) and `summarizer.py` (NLP logic). |
| `back_end_processing/` | Utilities for data cleaning, collection, and testing the IR search engine. |
| `models/` | Database models for `User` and `RecentSearch` data. |
| `templates/` | HTML interface components for a clean, user-friendly UI. |
| `data/` | Contains raw and processed academic materials used for the search engine. |

---

## **🧩 Requirements**

- **Python 3.11+**
- **Flask:** Web framework
- **Pandas/Numpy:** For data manipulation and vector calculations
- **NLTK:** For Natural Language Processing tasks
- **SQLAlchemy:** For database management

---

## **🚀 Usage**

### **1. Clone and Install**
```bash
git clone [https://github.com/buchanan97/notes-summarizer-app.git](https://github.com/buchanan97/notes-summarizer-app.git)
cd notes-summarizer-app
pip install -r requirements.txt
2. Prepare the Data
Run the preprocessing scripts to build the inverted index and document vectors:

Bash
python back_end_processing/collect_and_clean_data.py
3. Run the Application
Bash
python app.py
Access the web interface at http://127.0.0.1:5000

📝 Example Interaction
Search Query: "How does TCP/IP protocol work?"

The App Provides:

Top Matches: A list of textbook chapters from MIT and OpenStax specifically discussing networking.

Instant Summary: A 3-5 sentence summary of the top-ranked document explaining handshakes and data packets.

History: The query is saved to your dashboard for quick reference later.

🛡️ Technical Highlights
TF-IDF Calculation: Documents are ranked using Term Frequency-Inverse Document Frequency.

Cosine Similarity: Matches user queries to document vectors based on semantic closeness.

Modular Design: Backend IR services are decoupled from the frontend, allowing for easy updates to the search algorithm.

🤝 Contributing
Contributions are welcome! Whether you want to improve the summarization algorithm, add new document sources, or enhance the UI/UX, feel free to submit a pull reques
