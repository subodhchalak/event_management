import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from event.models import Event, Attendee


# -------------------------------- api_client -------------------------------- #


@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


# ----------------------------------- event ---------------------------------- #


@pytest.fixture
def event():
    return Event.objects.create(
        name="PyCon India",
        location="Pune",
        start_time=timezone.now() + timedelta(days=1),
        end_time=timezone.now() + timedelta(days=2),
        max_capacity=2
    )


# ----------------------------- attendee_payload ----------------------------- #

@pytest.fixture
def attendee_payload():
    return {
        "name": "John Doe",
        "email": "john@example.com"
    }


# -------------------------- second_attendee_payload ------------------------- #

@pytest.fixture
def second_attendee_payload():
    return {
        "name": "Jane Smith",
        "email": "jane@example.com"
    }


# ---------------------------- registered_attendee --------------------------- #

@pytest.fixture
def registered_attendee(event):
    return Attendee.objects.create(
        event=event,
        name="John Doe",
        email="john@example.com"
    )


# ---------------------------- test_list_attendees --------------------------- #


@pytest.mark.django_db
def test_list_attendees(api_client, event, registered_attendee):
    response = api_client.get(f"/events/{event.id}/attendees/")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["success"] is True
    assert response.data["data"][0]["email"] == "john@example.com"


# ---------------------- test_register_attendee_success ---------------------- #

@pytest.mark.django_db
def test_register_attendee_success(api_client, event, attendee_payload):
    response = api_client.post(
        f"/events/{event.id}/register/", 
        data=attendee_payload, 
        format="json"
    )
    assert response.status_code == status.HTTP_201_CREATED
    assert response.data["success"] is True
    assert response.data["data"]["email"] == attendee_payload["email"]


# ------------------ test_register_attendee_duplicate_email ------------------ #


@pytest.mark.django_db
def test_register_attendee_duplicate_email(api_client, event, registered_attendee):
    response = api_client.post(
        f"/events/{event.id}/register/", 
        data={"name": "John", "email": "john@example.com"}, 
        format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False


# -------------------- test_register_attendee_max_capacity ------------------- #

@pytest.mark.django_db
def test_register_attendee_max_capacity(api_client, event, attendee_payload, second_attendee_payload):
    # Fill capacity
    api_client.post(f"/events/{event.id}/register/", data=attendee_payload, format="json")
    api_client.post(f"/events/{event.id}/register/", data=second_attendee_payload, format="json")
    
    # Attempt third registration
    response = api_client.post(
        f"/events/{event.id}/register/", 
        data={"name": "Third", "email": "third@example.com"}, 
        format="json"
    )
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "event is full" in response.data["message"]


# ------------------- test_register_attendee_invalid_input ------------------- #

@pytest.mark.django_db
def test_register_attendee_invalid_input(api_client, event):
    # Missing required fields
    response = api_client.post(f"/events/{event.id}/register/", data={}, format="json")
    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert response.data["success"] is False
    assert "email" in response.data["errors"]
