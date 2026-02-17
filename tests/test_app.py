"""Tests for the Mergington High School Activities API"""

import pytest


class TestActivitiesEndpoint:
    """Tests for the GET /activities endpoint"""

    def test_get_activities_returns_200(self, client):
        """Test that GET /activities returns 200 status code"""
        response = client.get("/activities")
        assert response.status_code == 200

    def test_get_activities_returns_dict(self, client):
        """Test that GET /activities returns a dictionary"""
        response = client.get("/activities")
        assert isinstance(response.json(), dict)

    def test_get_activities_contains_expected_activities(self, client):
        """Test that all expected activities are returned"""
        response = client.get("/activities")
        activities = response.json()
        
        expected_activities = [
            "Basketball", "Tennis", "Debate Club", "Robotics Club",
            "Art Studio", "Music Ensemble", "Chess Club", "Programming Class", "Gym Class"
        ]
        
        for activity in expected_activities:
            assert activity in activities

    def test_activity_has_required_fields(self, client):
        """Test that each activity has required fields"""
        response = client.get("/activities")
        activities = response.json()
        
        required_fields = ["description", "schedule", "max_participants", "participants"]
        
        for activity_name, activity_data in activities.items():
            for field in required_fields:
                assert field in activity_data, f"Activity {activity_name} missing field {field}"

    def test_basketball_has_initial_participant(self, client):
        """Test that Basketball has james@mergington.edu as initial participant"""
        response = client.get("/activities")
        activities = response.json()
        assert "james@mergington.edu" in activities["Basketball"]["participants"]


class TestSignupEndpoint:
    """Tests for the POST /activities/{activity_name}/signup endpoint"""

    def test_signup_for_activity_returns_200(self, client):
        """Test that signup returns 200 status code for valid request"""
        response = client.post(
            "/activities/Basketball/signup?email=newstudent@mergington.edu"
        )
        assert response.status_code == 200

    def test_signup_adds_participant(self, client):
        """Test that signup adds participant to activity"""
        new_email = "newstudent@mergington.edu"
        client.post(f"/activities/Basketball/signup?email={new_email}")
        
        response = client.get("/activities")
        activities = response.json()
        assert new_email in activities["Basketball"]["participants"]

    def test_signup_returns_success_message(self, client):
        """Test that signup returns appropriate success message"""
        email = "newstudent@mergington.edu"
        response = client.post(f"/activities/Basketball/signup?email={email}")
        data = response.json()
        
        assert "message" in data
        assert email in data["message"]
        assert "Basketball" in data["message"]

    def test_signup_for_nonexistent_activity_returns_404(self, client):
        """Test that signup for non-existent activity returns 404"""
        response = client.post(
            "/activities/FakeActivity/signup?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_duplicate_returns_400(self, client):
        """Test that duplicate signup returns 400 error"""
        email = "james@mergington.edu"
        response = client.post(f"/activities/Basketball/signup?email={email}")
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_multiple_activities(self, client):
        """Test that student can sign up for multiple activities"""
        email = "multiactivity@mergington.edu"
        
        response1 = client.post(f"/activities/Basketball/signup?email={email}")
        assert response1.status_code == 200
        
        response2 = client.post(f"/activities/Tennis/signup?email={email}")
        assert response2.status_code == 200
        
        response = client.get("/activities")
        activities = response.json()
        assert email in activities["Basketball"]["participants"]
        assert email in activities["Tennis"]["participants"]


class TestUnregisterEndpoint:
    """Tests for the POST /activities/{activity_name}/unregister endpoint"""

    def test_unregister_returns_200(self, client):
        """Test that unregister returns 200 status code"""
        email = "james@mergington.edu"
        response = client.post(
            f"/activities/Basketball/unregister?email={email}"
        )
        assert response.status_code == 200

    def test_unregister_removes_participant(self, client):
        """Test that unregister removes participant from activity"""
        email = "james@mergington.edu"
        client.post(f"/activities/Basketball/unregister?email={email}")
        
        response = client.get("/activities")
        activities = response.json()
        assert email not in activities["Basketball"]["participants"]

    def test_unregister_returns_success_message(self, client):
        """Test that unregister returns appropriate success message"""
        email = "james@mergington.edu"
        response = client.post(
            f"/activities/Basketball/unregister?email={email}"
        )
        data = response.json()
        
        assert "message" in data
        assert email in data["message"]
        assert "Basketball" in data["message"]

    def test_unregister_nonexistent_activity_returns_404(self, client):
        """Test that unregister from non-existent activity returns 404"""
        response = client.post(
            "/activities/FakeActivity/unregister?email=student@mergington.edu"
        )
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_not_registered_returns_400(self, client):
        """Test that unregister for non-registered student returns 400"""
        response = client.post(
            "/activities/Basketball/unregister?email=notregistered@mergington.edu"
        )
        assert response.status_code == 400
        assert "not signed up" in response.json()["detail"]

    def test_unregister_and_signup_again(self, client):
        """Test that student can unregister and sign up again"""
        email = "testuser@mergington.edu"
        activity = "Tennis"
        
        # Sign up
        response1 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200
        
        # Unregister
        response2 = client.post(f"/activities/{activity}/unregister?email={email}")
        assert response2.status_code == 200
        
        # Sign up again
        response3 = client.post(f"/activities/{activity}/signup?email={email}")
        assert response3.status_code == 200
        
        # Verify registered
        response = client.get("/activities")
        activities = response.json()
        assert email in activities[activity]["participants"]


class TestRootEndpoint:
    """Tests for the root endpoint"""

    def test_root_returns_redirect(self, client):
        """Test that root endpoint returns a redirect"""
        response = client.get("/", follow_redirects=False)
        assert response.status_code == 307


class TestIntegration:
    """Integration tests combining multiple endpoints"""

    def test_full_signup_workflow(self, client):
        """Test complete signup workflow"""
        # Get initial state
        response = client.get("/activities")
        initial_basketball = response.json()["Basketball"]["participants"].copy()
        
        email = "workflow@mergington.edu"
        
        # Sign up
        response = client.post(f"/activities/Basketball/signup?email={email}")
        assert response.status_code == 200
        
        # Verify signed up
        response = client.get("/activities")
        assert email in response.json()["Basketball"]["participants"]
        
        # Unregister
        response = client.post(f"/activities/Basketball/unregister?email={email}")
        assert response.status_code == 200
        
        # Verify unregistered
        response = client.get("/activities")
        assert email not in response.json()["Basketball"]["participants"]

    def test_activity_capacity_not_enforced(self, client):
        """Test that current API doesn't enforce max_participants limit"""
        # This test documents current behavior - capacity is not enforced
        activity = "Basketball"
        response = client.get("/activities")
        max_participants = response.json()[activity]["max_participants"]
        
        # Add many students
        for i in range(max_participants + 5):
            email = f"student{i}@mergington.edu"
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200
        
        # Verify all were added
        response = client.get("/activities")
        participants = response.json()[activity]["participants"]
        assert len(participants) > max_participants
