import os
import sys
import threading
import webview
from flask import Flask
from extensions import db, login_manager
from routes import main_bp 
from APP.services.ir_engine import IREngine
from APP.services.summarizer import Summarizer

project_root = os.path.abspath(os.path.dirname(__file__))
if project_root not in sys.path:
    sys.path.append(project_root)

DATABASE_DIR = os.path.join(project_root, 'data')
DATABASE_FILE = os.path.join(DATABASE_DIR, 'app.db')

os.makedirs(DATABASE_DIR, exist_ok=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'a_very_secret_key_for_dev'
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL') or f'sqlite:///{DATABASE_FILE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    FLASK_DEBUG = True


def create_app():
    app = Flask(__name__,
                template_folder='templates',
                static_folder='static')
    app.config.from_object(Config)

    db.init_app(app)
    login_manager.init_app(app)
    login_manager.login_view = 'main.main_screen'

    from models.user import User
    @login_manager.user_loader
    def load_user(user_id):
        return db.session.execute(db.select(User).filter_by(id=user_id)).scalar_one_or_none()

    app.register_blueprint(main_bp)

    with app.app_context():
        db.create_all()

        try:
            processed_data_path = os.path.join(project_root, "data", "processed_data")
            if not os.path.exists(processed_data_path) or not os.listdir(processed_data_path):
                print(f"WARNING: No processed data found at {processed_data_path}. "
                      f"Please run 'python3 back_end_processing/collect_and_clean_data.py' first.")
                app.config['IR_ENGINE'] = None
                app.config['SUMMARIZER'] = None
            else:
                app.config['IR_ENGINE'] = IREngine(processed_data_path)
                app.config['SUMMARIZER'] = Summarizer()
                print("IR Engine and Summarizer initialized successfully.")
        except Exception as e:
            print(f"CRITICAL ERROR: Failed to initialize IR Engine or Summarizer: {e}")
            app.config['IR_ENGINE'] = None
            app.config['SUMMARIZER'] = None
    return app

def run_flask():
    app_instance = create_app()
    app_instance.run(debug=False, use_reloader=False)

if __name__ == '__main__':
    if 'DISPLAY' in os.environ or os.getenv('WSL_DISTRO_NAME') or sys.platform == 'darwin':
        threading.Thread(target=run_flask, daemon=True).start()
        import time
        time.sleep(1)
        webview.create_window('Notes Summarizer', 'http://127.0.0.1:5000')
        webview.start()
    else:
        print("No graphical display found. Running Flask in console mode.")
        run_flask()