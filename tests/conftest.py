"""
Pytest configuration and fixtures for testing the FastAPI application
"""
import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient

# Add src directory to Python path so we can import app
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from app import app, activities


@pytest.fixture
def client():
    """Create a test client for the FastAPI application"""
    return TestClient(app)


@pytest.fixture
def reset_activities():
    """Reset activities to known state before and after each test"""
    original_activities = {
        activity_name: {
            **details,
            "participants": details["participants"].copy()
        }
        for activity_name, details in activities.items()
    }
    
    yield
    
    # Reset activities after test
    activities.clear()
    activities.update(original_activities)
