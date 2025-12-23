# Database Singleton - Ensures only one database instance exists

from flask_sqlalchemy import SQLAlchemy

class DatabaseSingleton: # Singleton pattern for database instance
    _instance = None
    _db = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseSingleton, cls).__new__(cls)
            cls._db = SQLAlchemy()
        return cls._instance
    
    @property
    def db(self): # Get the database instance
        return self._db
    
    def init_app(self, app): # Initialize the database with Flask app
        self._db.init_app(app)
        return self._db


database = DatabaseSingleton()
