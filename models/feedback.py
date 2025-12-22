from app import db

class Feedback(db.Model):
    __tablename__ = 'feedback'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)  # Nullable for anonymous feedback
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), nullable=False)
    subject = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=False)
    feedback_type = db.Column(db.String(50), default='general')  # general, support, feedback, complaint, suggestion
    status = db.Column(db.String(50), default='new')  # new, read, responded, resolved
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())
    updated_at = db.Column(db.DateTime, default=db.func.current_timestamp(), onupdate=db.func.current_timestamp())
    
    # Relationship
    user = db.relationship('User', backref='feedbacks', lazy=True)
    
    def __repr__(self):
        return f'<Feedback {self.id} - {self.subject} - {self.status}>'



