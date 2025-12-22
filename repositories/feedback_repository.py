# Feedback Repository - Handles all data access for Feedback entity

from .base_repository import BaseRepository
from models.feedback import Feedback

class FeedbackRepository(BaseRepository): # Repository for Feedback entity    
    def __init__(self):
        super().__init__(Feedback)
    
    def get_by_status(self, status): # Get feedback by status
        return self.filter_by(status=status).all()
    
    def get_by_type(self, feedback_type): # Get feedback by type
        return self.filter_by(feedback_type=feedback_type).all()
    
    def get_by_user_id(self, user_id): # Get all feedback by a user
        return self.filter_by(user_id=user_id).all()
    
    def create_feedback(self, feedback): # Create a new feedback
        return self.create(feedback)
    
    def update_feedback(self, feedback): # Update an existing feedback
        return self.update(feedback)
    
    def delete_feedback(self, feedback): # Delete a feedback
        self.delete(feedback)



