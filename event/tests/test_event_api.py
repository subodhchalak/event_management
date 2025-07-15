import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..')))


import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from event.models import Event

EVENT_LIST_URL = "/events/"


# -------------------------------- api_client -------------------------------- #

@pytest.fixture
def api_client():
    from rest_framework.test import APIClient
    return APIClient()


# ------------------------------- future_event ------------------------------- #


@pytest.fixture
def future_event():
    return Event.objects.create(
        name="Test Conference",
        location="Mumbai",
        start_time=timezone.now() + timedelta(days=2),
        end_time=timezone.now() + timedelta(days=3),
        max_capacity=100,
    )

# ------------------------------- event_payload ------------------------------ #


@pytest.fixture
def event_payload():
    return {
        "name": "AI Summit",
        "location": "Bangalore",
        "start_time": "2025-07-25 12:00:00",
        "end_time": "2025-07-27 18:30:00",
        "max_capacity": 150
    }


# ----------------------------- test_list_events ----------------------------- #


@pytest.mark.django_db
def test_list_events(api_client, future_event):
    response = api_client.get(EVENT_LIST_URL, HTTP_X_TIMEZONE="Asia/Kolkata")
    print(f"test_list_events response: {response.data}")
    assert response.status_code == status.HTTP_200_OK


# ---------------------------- test_retrieve_event --------------------------- #


@pytest.mark.django_db
def test_retrieve_event(api_client, future_event):
    response = api_client.get(f"/events/{future_event.id}/", HTTP_X_TIMEZONE="Asia/Kolkata")
    print(f"test_retrieve_event response: {response.data}")
    assert response.status_code == status.HTTP_200_OK
    assert response.data["data"]["name"] == future_event.name


# ----------------------------- test_create_event ---------------------------- #


@pytest.mark.django_db
def test_create_event(api_client, event_payload):
    response = api_client.post(EVENT_LIST_URL, data=event_payload, format="json", HTTP_X_TIMEZONE="Asia/Kolkata")
    print(f"test_create_event response: {response.data}")
    assert response.status_code == status.HTTP_201_CREATED


# # ------------------------- test_create_event_invalid ------------------------ #


@pytest.mark.django_db
def test_create_event_invalid(api_client):
    bad_data = {
        "name": "",  # empty, should fail
        "location": "Pune",
        "start_time": "2024-07-20 12:00:00",  # invalid datetime
        "end_time": "2025-07-20 12:00:00",  # may still be valid
        "max_capacity": -5  # invalid
    }
    response = api_client.post("/events/", data=bad_data, format="json", HTTP_X_TIMEZONE="Asia/Kolkata")
    print(f"test_create_event_invalid response: {response}")
    assert response.status_code == 400
    assert "errors" in response.data


# # ----------------------------- test_update_event ---------------------------- #


# @pytest.mark.django_db
# def test_update_event(api_client, future_event):
#     updated_data = {
#         "name": "Updated Conference",
#         "location": future_event.location,
#         "start_time": "2025-08-10 15:00:00",
#         "end_time": "2025-08-12 17:00:00",
#         "max_capacity": future_event.max_capacity
#     }
#     print(f"test_update_event updated_data: {updated_data}")
#     print(f"test_update_event future_event.id: {future_event.id}")
#     response = api_client.put(f"/events/{future_event.id}/", data=updated_data, format="json", HTTP_X_TIMEZONE="Asia/Kolkata")
#     print(f"test_update_event response: {response}")
#     # assert response.status_code == status.HTTP_200_OK
#     # assert response.data["data"]["name"] == "Updated Conference"



