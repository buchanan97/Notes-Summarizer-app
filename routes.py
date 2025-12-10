import os
import re
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from models.recent_search import RecentSearch
from models.user import User
from extensions import db

main_bp = Blueprint('main', __name__)


def clean_text(text):
    if not text:
        return ""
    text = re.sub(r"[■□▪▫◼◻▢▣�]", "", text)  
    text = re.sub(r"\s+", " ", text)  
    return text.strip()


def clean_display_title(filename):
    
    filename = filename.replace(".txt", "")
    filename = re.sub(r"_chunk_\d+", "", filename)

    filename = re.sub(r"^[a-fA-F0-9]{32}_", "", filename)

    mit_match = re.match(r"(MIT)(\d+)[-_](\d+[A-Z]?\d*)[_-](Lec)(\d+)", filename)
    if mit_match:
        course = mit_match.group(2)
        lecture = mit_match.group(5)
        return f"MIT {course} Lecture {lecture}"

    return filename.replace("_", " ").strip()


def extract_heading(paragraph):
    if not paragraph:
        return None

    patterns = [
        r"(Chapter\s+\d+[:\-\s]+[A-Za-z].+)",
        r"(Section\s+\d+[:\-\s]+[A-Za-z].+)",
        r"(\b\d+\.\d+\s+[A-Z][A-Za-z\s]+)",
        r"(\b\d+\s+[A-Z][A-Za-z\s]+)"
    ]

    for p in patterns:
        m = re.search(p, paragraph)
        if m:
            return m.group(1).strip()

    return None


def enforce_min_sentences(text, minimum=3):
    sentences = re.split(r"(?<=[.!?])\s+", text)
    if len(sentences) >= minimum:
        return text
    return " ".join(sentences[:minimum])


@main_bp.route('/')
def welcome_page():
   return render_template('welcome_screen.html')


@main_bp.route('/search')
def search_input_page():
    user_id = current_user.id if current_user.is_authenticated else None
    recent_searches_list = []

    if user_id:
        recent_searches_list = db.session.execute(
            select(RecentSearch)
            .filter_by(user_id=user_id)
            .order_by(RecentSearch.timestamp.desc())
            .limit(10)
        ).scalars().all()

    return render_template('search_screen.html', recent_searches=recent_searches_list)


@main_bp.route('/perform_search', methods=['POST'])
def perform_search_api():
    query = request.form.get('query')
    if not query:
        return jsonify({"error": "Query cannot be empty"}), 400

    ir_engine = current_app.config.get('IR_ENGINE')
    summarizer = current_app.config.get('SUMMARIZER')

    if ir_engine is None or summarizer is None:
        return jsonify({"error": "Search service unavailable"}), 500

    top_documents = ir_engine.search(query)
    results = []

    if current_user.is_authenticated:
        new_search = RecentSearch(user_id=current_user.id, query_text=query)
        db.session.add(new_search)
        db.session.commit()

    for doc_data in top_documents:

        filepath = doc_data["filename"]

        raw_paragraph = clean_text(doc_data["paragraph"])
        score = doc_data["score"]

        display_title = clean_display_title(filepath.split("/")[-1])
        heading = extract_heading(raw_paragraph)

        if heading:
            full_title = f"{display_title} — {heading}"
        else:
            full_title = display_title

        snippet = summarizer.summarize(raw_paragraph, query)
        snippet = clean_text(snippet)
        snippet = enforce_min_sentences(snippet, minimum=3)

        if not snippet or len(snippet) < 50:
            fallback_len = 280
            snippet = raw_paragraph[:fallback_len].rsplit(" ", 1)[0] + "..."

        lower_path = filepath.lower()

        if "reading_materials" in lower_path or "materials" in lower_path:
            source_label = "B.Tech CS Materials"
        elif "mit_opencourseware" in lower_path:
            source_label = "MIT OpenCourseWare"
        elif "openstax" in lower_path:
            source_label = "OpenStax"
        elif "opentextbooklibrary" in lower_path or "opentextbook" in lower_path:
            source_label = "Open Textbook Library"
        else:
            source_label = "General Resource"

        results.append({
            "display_filename": full_title,
            "filename": filepath,
            "source": source_label,
            "snippet": snippet,
            "score": f"{score:.4f}"
        })


    return jsonify(results=results, query=query)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.search_input_page'))

    if request.method == 'POST':
        email = request.form.get('email')
        password = request.form.get('password')

        user = db.session.execute(db.select(User).filter_by(email=email)).scalar_one_or_none()

        if user is None or not user.check_password(password):
            flash("Invalid email or password.", "error")
            return render_template('login_screen.html', email=email) 
        
        login_user(user, remember=True) 
        flash(f"Welcome back, {user.username}!", "success")
        
        return redirect(url_for('main.search_input_page'))
    
    return render_template('login_screen.html') 


@main_bp.route('/signup', methods=['GET', 'POST'])
def signup():
    if current_user.is_authenticated:
        flash("You are already logged in.", "info")
        return redirect(url_for('main.search_input_page'))

    if request.method == 'POST':
        name = request.form.get('name') 
        email = request.form.get('email')
        password = request.form.get('password')
        confirm_password = request.form.get('confirm_password') 

        if password != confirm_password:
            flash("Passwords do not match.", "error")
            return render_template('signup_screen.html', email=email, name=name)

        try:
            existing = db.session.execute(
                db.select(User).filter((User.username == name) | (User.email == email))
            ).scalar()

            if existing:
                flash("An account with that username or email already exists.", "error")
                return render_template('signup_screen.html', email=email, name=name)

            new_user = User(username=name, email=email)
            new_user.set_password(password)

            db.session.add(new_user)
            db.session.commit()

            flash("Account created successfully! Please log in.", "success")
            return redirect(url_for('main.login'))

        except IntegrityError:
            db.session.rollback()
            flash("Database error occurred.", "error")
            return render_template('signup_screen.html', email=email, name=name)

    return render_template('signup_screen.html')


@main_bp.route('/logout')
def logout_user_route():
    if current_user.is_authenticated:
        logout_user()
        flash("You have been logged out.", "info")
    return redirect(url_for('main.welcome_page'))



@main_bp.route('/view_doc/<path:doc_filename>')
def view_doc(doc_filename):
    ir_engine = current_app.config.get('IR_ENGINE')

    if ir_engine is None:
        flash("Search engine unavailable.", "error")
        return redirect(url_for('main.search_input_page'))

    full_text = ir_engine.get_document_text(doc_filename)

    if full_text:
        return render_template(
            'full_text_view.html',
            filename=doc_filename.replace('.txt', ''),
            text=full_text
        )
    else:
        flash(f"Document '{doc_filename}' not found.", "error")
        return redirect(url_for('main.search_input_page'))
