from extensions import db
import datetime

class RecentSearch(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    # This is the line that needs to be correct to match 'query_text'
    query_text = db.Column(db.String(500), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.datetime.utcnow)

    def __repr__(self):
        return f'<RecentSearch {self.query_text} by User {self.user_id}>'