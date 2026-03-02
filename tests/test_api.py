"""
Tests for the FastAPI activity management API.
Uses the AAA (Arrange-Act-Assert) pattern for test structure.
"""

import pytest
from fastapi.testclient import TestClient


class TestGetActivities:
    """Tests for the GET /activities endpoint."""

    def test_get_activities_returns_all_activities(self, client, reset_activities):
        """
        Test that GET /activities returns all activities with details.
        
        AAA Pattern:
        - Arrange: client fixture already set up
        - Act: send GET request to /activities
        - Assert: verify response status and data
        """
        # Act
        response = client.get("/activities")

        # Assert
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, dict)
        assert len(data) == 9
        assert "Chess Club" in data

    def test_get_activities_returns_activity_details(self, client, reset_activities):
        """
        Test that activity details are correctly returned.
        
        AAA Pattern:
        - Arrange: client fixture already set up
        - Act: send GET request to /activities
        - Assert: verify activity structure
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        chess_club = data["Chess Club"]
        assert chess_club["description"] == "Learn strategies and compete in chess tournaments"
        assert chess_club["schedule"] == "Fridays, 3:30 PM - 5:00 PM"
        assert chess_club["max_participants"] == 12
        assert isinstance(chess_club["participants"], list)
        assert len(chess_club["participants"]) == 2

    def test_get_activities_participants_list(self, client, reset_activities):
        """
        Test that participants are correctly displayed.
        
        AAA Pattern:
        - Arrange: client fixture already set up
        - Act: send GET request to /activities
        - Assert: verify participants data
        """
        # Act
        response = client.get("/activities")
        data = response.json()

        # Assert
        chess_participants = data["Chess Club"]["participants"]
        assert "michael@mergington.edu" in chess_participants
        assert "daniel@mergington.edu" in chess_participants


class TestSignupForActivity:
    """Tests for the POST /activities/{activity_name}/signup endpoint."""

    def test_signup_new_participant_success(self, client, reset_activities):
        """
        Test successful signup of a new participant.
        
        AAA Pattern:
        - Arrange: prepare email and activity (via fixture)
        - Act: send POST request to signup endpoint
        - Assert: verify success response and participant added
        """
        # Arrange
        email = "newstudent@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Signed up {email} for {activity}"
        
        # Verify participant was added
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity]["participants"]
        assert email in participants

    def test_signup_duplicate_participant_fails(self, client, reset_activities):
        """
        Test that signing up an already registered participant fails.
        
        AAA Pattern:
        - Arrange: use existing participant from fixture
        - Act: send POST request to signup endpoint
        - Assert: verify error response
        """
        # Arrange
        email = "michael@mergington.edu"  # Already in Chess Club
        activity = "Chess Club"

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 400
        assert "already signed up" in response.json()["detail"]

    def test_signup_nonexistent_activity_fails(self, client, reset_activities):
        """
        Test that signup fails for non-existent activities.
        
        AAA Pattern:
        - Arrange: prepare invalid activity name
        - Act: send POST request to signup endpoint
        - Assert: verify 404 error
        """
        # Arrange
        email = "student@mergington.edu"
        activity = "NonExistentClub"

        # Act
        response = client.post(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_signup_multiple_different_activities(self, client, reset_activities):
        """
        Test that a student can sign up for multiple different activities.
        
        AAA Pattern:
        - Arrange: prepare email and multiple activities
        - Act: send multiple POST requests
        - Assert: verify student appears in all activities
        """
        # Arrange
        email = "multisport@mergington.edu"
        activities_to_join = ["Chess Club", "Basketball", "Drama Club"]

        # Act
        for activity in activities_to_join:
            response = client.post(
                f"/activities/{activity}/signup?email={email}"
            )
            assert response.status_code == 200

        # Assert
        all_activities = client.get("/activities").json()
        for activity in activities_to_join:
            assert email in all_activities[activity]["participants"]


class TestUnregisterFromActivity:
    """Tests for the DELETE /activities/{activity_name}/signup endpoint."""

    def test_unregister_participant_success(self, client, reset_activities):
        """
        Test successful unregistration of a participant.
        
        AAA Pattern:
        - Arrange: prepare existing participant email
        - Act: send DELETE request to unregister endpoint
        - Assert: verify success and participant removed
        """
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 200
        assert response.json()["message"] == f"Unregistered {email} from {activity}"
        
        # Verify participant was removed
        activities_response = client.get("/activities")
        participants = activities_response.json()[activity]["participants"]
        assert email not in participants

    def test_unregister_nonexistent_participant_fails(self, client, reset_activities):
        """
        Test that unregistering a non-existent participant fails.
        
        AAA Pattern:
        - Arrange: prepare non-existent participant email
        - Act: send DELETE request to unregister endpoint
        - Assert: verify 404 error
        """
        # Arrange
        email = "notregistered@mergington.edu"
        activity = "Chess Club"

        # Act
        response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "not registered" in response.json()["detail"]

    def test_unregister_from_nonexistent_activity_fails(self, client, reset_activities):
        """
        Test that unregistering from non-existent activity fails.
        
        AAA Pattern:
        - Arrange: prepare invalid activity name
        - Act: send DELETE request to unregister endpoint
        - Assert: verify 404 error
        """
        # Arrange
        email = "student@mergington.edu"
        activity = "NonExistentClub"

        # Act
        response = client.delete(
            f"/activities/{activity}/signup?email={email}"
        )

        # Assert
        assert response.status_code == 404
        assert "Activity not found" in response.json()["detail"]

    def test_unregister_multiple_times_fails(self, client, reset_activities):
        """
        Test that unregistering twice fails on second attempt.
        
        AAA Pattern:
        - Arrange: prepare existing participant
        - Act: send DELETE request twice
        - Assert: first succeeds, second fails
        """
        # Arrange
        email = "michael@mergington.edu"
        activity = "Chess Club"

        # Act & Assert - First unregister succeeds
        response1 = client.delete(f"/activities/{activity}/signup?email={email}")
        assert response1.status_code == 200

        # Act & Assert - Second unregister fails
        response2 = client.delete(f"/activities/{activity}/signup?email={email}")
        assert response2.status_code == 404
        assert "not registered" in response2.json()["detail"]


class TestRootEndpoint:
    """Tests for the GET / endpoint."""

    def test_root_redirects_to_static(self, client):
        """
        Test that root path redirects to static HTML.
        
        AAA Pattern:
        - Arrange: client fixture already set up
        - Act: send GET request to /
        - Assert: verify redirect response
        """
        # Act
        response = client.get("/", follow_redirects=False)

        # Assert
        assert response.status_code == 307
        assert "/static/index.html" in response.headers["location"]
