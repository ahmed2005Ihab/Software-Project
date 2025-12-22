from abc import ABC, abstractmethod
from core.database import database

class BaseRepository(ABC):
    #Base repository class that all repositories inherit from
    
    def __init__(self, model_class):
        self.model_class = model_class
        self.db = database.db
    
    def get_by_id(self, id):
        return self.db.session.query(self.model_class).get(id)
    
    def get_all(self):
        return self.db.session.query(self.model_class).all()
    
    def create(self, entity):
        self.db.session.add(entity)
        self.db.session.commit()
        self.db.session.refresh(entity)
        return entity
    
    def update(self, entity):
        self.db.session.commit()
        self.db.session.refresh(entity)
        return entity
    
    def delete(self, entity):
        self.db.session.delete(entity)
        self.db.session.commit()
    
    def filter_by(self, **kwargs):
        return self.db.session.query(self.model_class).filter_by(**kwargs)
    
    def query(self):
        return self.db.session.query(self.model_class)



