from flask import Flask, render_template, request, redirect, url_for
from APP.services.ir_engine import IREngine
from flask import Flask, render_template, request
from APP.services.ir_engine import IREngine
from APP.services.summarizer import summarizer
import os

app = Flask(__name__)

PROCESSED_DIR = "APP/data/processed_data"
docs = []
filenames = []

for file in os.listdir(PROCESSED_DIR):
    if file.endswith(".txt"):
        with open(os.path.join(PROCESSED_DIR, file), "r", encoding="utf-8") as f:
            docs.append(f.read())
            filenames.append(file)

ir = IREngine(docs)
sumr = summarizer()

@app.route("/")
def welcome():
    return render_template("welcome_screen.html")

@app.route("/search", methods=["GET", "POST"])
def search():
    if request.method == "POST":
        query = request.form["query"]
        # Here you can call IR engine when ready
        results = []  # placeholder
        return render_template("results_screen.html", query=query, results=results)
    return render_template("search_screen.html")

if __name__ == "__main__":
    app.run(debug=True)