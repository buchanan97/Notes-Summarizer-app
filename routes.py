import os
import sys
from flask import Blueprint, render_template, request, jsonify, current_app, redirect, url_for, flash
from flask_login import login_required, current_user, login_user, logout_user
from sqlalchemy import select
from models.recent_search import RecentSearch
from models.user import User
from extensions import db


main_bp = Blueprint('main', __name__)

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


   # --- GET IR_ENGINE AND SUMMARIZER FROM CURRENT_APP.CONFIG ---
   ir_engine = current_app.config.get('IR_ENGINE')
   summarizer = current_app.config.get('SUMMARIZER')


   if ir_engine is None or summarizer is None:
       return jsonify({"error": "Search service is not available. Please check server logs for initialization errors."}), 500


   top_documents = ir_engine.search(query)
   results = []


   if current_user.is_authenticated:
       new_search = RecentSearch(user_id=current_user.id, query_text=query)
       db.session.add(new_search)
       db.session.commit()
   else:
       print("WARNING: Not saving search query as user is not authenticated.")


   for doc_data in top_documents:
       score = doc_data["score"]
       raw_best_paragraph = doc_data["paragraph"]
       original_filename = doc_data["filename"]

       search_snippet = ""
       if raw_best_paragraph:
        search_snippet = summarizer.summarize(raw_best_paragraph, sentence_count=2) # <--- Generate a 2-sentence summary
       if not search_snippet or len(search_snippet) < 50: # Example: ensure a minimum length
            max_fallback_length = 300
            if len(raw_best_paragraph) > max_fallback_length:
                search_snippet = raw_best_paragraph[:max_fallback_length].rsplit(' ', 1)[0] + '...'
            else:
                search_snippet = raw_best_paragraph

       results.append({
           'display_filename': original_filename.replace('.txt', ''),
           'filename': original_filename,
           'source': 'Textbook',
           'summary': None,
           'snippet': search_snippet,
           'doc_id': original_filename,
           'score': f"{score:.4f}",
       })


   return jsonify(results=results, query=query)


@main_bp.route('/login', methods=['GET', 'POST'])
def login():
   if not current_user.is_authenticated:
       dummy_user = db.session.execute(db.select(User).filter_by(username='testuser')).scalar_one_or_none()
       if not dummy_user:
           dummy_user = User(username='testuser', email='test@example.com')
           dummy_user.set_password('password')
           db.session.add(dummy_user)
           db.session.commit()


       login_user(dummy_user)
       flash("Logged in as testuser (dummy login).", "info")
       return redirect(url_for('main.search_input_page'))


   return redirect(url_for('main.search_input_page'))


@main_bp.route('/logout')
def logout_user_route():
   if current_user.is_authenticated:
       logout_user()
       flash("You have been logged out.", "info")
   return redirect(url_for('main.welcome_page'))

# In notes-summarizer-app/routes.py, inside view_doc function

@main_bp.route('/view_doc/<path:doc_filename>')
def view_doc(doc_filename):
    ir_engine = current_app.config.get('IR_ENGINE')
    #summarizer = current_app.config.get('SUMMARIZER') # <--- IMPORTANT: Re-enable summarizer here

    # Check both services now that summarizer is used here
    if ir_engine is None:
        flash("Search services not available. Please check server logs for initialization errors.", "error")
        return redirect(url_for('main.search_input_page'))

    full_text = ir_engine.get_document_text(doc_filename)
    if full_text:
        #document_summary = summarizer.summarize(full_text) # <--- Generate summary here
        return render_template('full_text_view.html',
                               filename=doc_filename.replace('.txt', ''),
                               text=full_text
                               )
    else:
        flash(f"Document '{doc_filename}' not found or could not be read.", "error")
        return redirect(url_for('main.search_input_page'))