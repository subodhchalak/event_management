# django imports
from django.urls import path, include
from rest_framework.routers import DefaultRouter

# in-app imports
from event.views import (
    EventModelViewSet,
    AttendeeModelViewset,
)


# Create a router and register our ViewSets with it.
router = DefaultRouter()
router.register(r'events', EventModelViewSet, basename='events')


# The API URLs are now determined automatically by the router.

urlpatterns = [
    path('', include(router.urls)),
    # Manually add the nested URL for attendees of a specific event
    path('events/<int:event_id>/attendees/', AttendeeModelViewset.as_view({'get': 'list'}), name='attendee-list'),
    path('events/<int:event_id>/register/', AttendeeModelViewset.as_view({'post': 'create'}), name='attendee-create')
]