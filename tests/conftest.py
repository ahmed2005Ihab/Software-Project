import pytest
import sys
import os
# Ensure project root is on sys.path so 'app' package can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from app import create_app

# Instantiate the Flask app here to avoid circular imports
app = create_app()


@pytest.fixture
def client():
 app.config['TESTING'] = True
 return app.test_client()