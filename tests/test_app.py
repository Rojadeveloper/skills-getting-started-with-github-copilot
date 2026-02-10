"""
Tests for the Mergington High School Activities API
"""
import pytest


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""
    
    def test_get_activities_returns_all_activities(self, client):
        """Test that all activities are returned"""
        response = client.get("/activities")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) > 0
        assert "Basketball Team" in data
        assert "Tennis" in data
    
    def test_activity_has_required_fields(self, client):
        """Test that activities have all required fields"""
        response = client.get("/activities")
        data = response.json()
        activity = data["Basketball Team"]
        
        assert "description" in activity
        assert "schedule" in activity
        assert "max_participants" in activity
        assert "participants" in activity


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""
    
    def test_signup_new_participant(self, client, reset_activities):
        """Test signing up a new participant for an activity"""
        new_email = "newstudent@mergington.edu"
        response = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": new_email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "message" in data
        assert new_email in data["message"]
        
        # Verify participant was added
        response = client.get("/activities")
        activities = response.json()
        assert new_email in activities["Basketball Team"]["participants"]
    
    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """Test that signing up twice for same activity fails"""
        email = "alex@mergington.edu"
        response = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "already signed up" in data["detail"]
    
    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """Test that signing up for non-existent activity fails"""
        response = client.post(
            "/activities/Fake%20Activity/signup",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]
    
    def test_signup_multiple_different_activities(self, client, reset_activities):
        """Test that a student can sign up for multiple different activities"""
        email = "newstudent@mergington.edu"
        
        # Sign up for first activity
        response1 = client.post(
            "/activities/Basketball%20Team/signup",
            params={"email": email}
        )
        assert response1.status_code == 200
        
        # Sign up for second activity
        response2 = client.post(
            "/activities/Tennis/signup",
            params={"email": email}
        )
        assert response2.status_code == 200
        
        # Verify both signups succeeded
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Basketball Team"]["participants"]
        assert email in activities["Tennis"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""
    
    def test_unregister_existing_participant(self, client, reset_activities):
        """Test unregistering an existing participant"""
        email = "alex@mergington.edu"
        response = client.post(
            "/activities/Basketball%20Team/unregister",
            params={"email": email}
        )
        
        assert response.status_code == 200
        data = response.json()
        assert "Unregistered" in data["message"]
        
        # Verify participant was removed
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Basketball Team"]["participants"]
    
    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """Test that unregistering non-existent participant fails"""
        response = client.post(
            "/activities/Basketball%20Team/unregister",
            params={"email": "notregistered@mergington.edu"}
        )
        
        assert response.status_code == 400
        data = response.json()
        assert "not registered" in data["detail"]
    
    def test_unregister_from_nonexistent_activity_fails(self, client, reset_activities):
        """Test that unregistering from non-existent activity fails"""
        response = client.post(
            "/activities/Fake%20Activity/unregister",
            params={"email": "student@mergington.edu"}
        )
        
        assert response.status_code == 404
        data = response.json()
        assert "not found" in data["detail"]


class TestIntegrationScenarios:
    """Integration tests for realistic usage scenarios"""
    
    def test_full_signup_flow(self, client, reset_activities):
        """Test complete signup flow: signup, verify, unregister, verify"""
        email = "integration@mergington.edu"
        activity = "Chess%20Club"
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify signup
        response = client.get("/activities")
        activities_data = response.json()
        assert email in activities_data["Chess Club"]["participants"]
        
        # Unregister
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Verify unregister
        response = client.get("/activities")
        activities_data = response.json()
        assert email not in activities_data["Chess Club"]["participants"]
    
    def test_cannot_signup_after_unregister_then_signup_again(self, client, reset_activities):
        """Test that a student can re-register after unregistering"""
        email = "reregister@mergington.edu"
        activity = "Art%20Club"
        
        # Sign up
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Unregister
        response = client.post(
            f"/activities/{activity}/unregister",
            params={"email": email}
        )
        assert response.status_code == 200
        
        # Sign up again
        response = client.post(
            f"/activities/{activity}/signup",
            params={"email": email}
        )
        assert response.status_code == 200
