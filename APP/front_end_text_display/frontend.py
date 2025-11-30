from flask import Flask, render_template, request, redirect, url_for, session
from APP.services.ir_engine import IREngine
from APP.services.summarizer import Summarizer
import os
import threading
import webbrowser
import time

app = Flask(__name__)
app.secret_key = "supersecretkey"

PROCESSED_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "data", "processed_data"))
ir = IREngine(PROCESSED_DIR)
sumr = Summarizer()

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username")
        password = request.form.get("password")
        if username == "test" and password == "password":
            session["logged_in"] = True
            session["username"] = username
            return redirect(url_for("search"))
        return render_template("login.html", error="Invalid username or password")
    return render_template("login.html")

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("welcome"))

@app.route("/")
def welcome():
    return render_template("welcome_screen.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form["query"]
        results = ir.search(query)
        for r in results:
            r["summary"] = sumr.summarize(r["paragraph"]) or "Summary unavailable."
        return render_template("results_screen.html", query=query, results=results)
    return render_template("search_screen.html")

@app.route("/view/<doc_id>")
def view_doc(doc_id):
    doc = ir.get_document_by_id(doc_id)
    if not doc:
        return "Document not found", 404

    filename = doc.get("filename") or f"Document {doc_id}"
    text = doc.get("text") or "No content available."

    summary = doc.get("summary")
    if not summary:
        summary = sumr.summarize(text) or "Summary unavailable."

    return render_template("full_text_view.html", filename=filename, text=text, summary=summary)

def run_flask():
    app.run(debug=False, port=5000, use_reloader=False)

if __name__ == "__main__":
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    time.sleep(1)
    webbrowser.open("http://127.0.0.1:5000")
    while True:
        time.sleep(1)

