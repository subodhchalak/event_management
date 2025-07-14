# django imports
from django.db import models


# ---------------------------------------------------------------------------- #
#                                     Event                                    #
# ---------------------------------------------------------------------------- #


class Event(models.Model):
    """
    Represents an event that can be attended.

    Attributes:
        name (str): The name of the event. Must be unique.
        location (str): The location where the event is held.
        start_time (datetime): The start date and time of the event.
        end_time (datetime): The end date and time of the event.
        max_capacity (int): The maximum number of attendees for the event.
        created_at (datetime): The timestamp when the event was created.
        updated_at (datetime): The timestamp when the event was last updated.
    """
    name = models.CharField(max_length=255, unique=True)
    location = models.CharField(max_length=255)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    max_capacity = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the Event model."""
        ordering = ('-id', )

    def __str__(self):
        """Returns a string representation of the event."""
        return f"Event-{str(self.id).zfill(6)}-{self.name}"



# ---------------------------------------------------------------------------- #
#                                   Attendee                                   #
# ---------------------------------------------------------------------------- #


class Attendee(models.Model):
    """
    Represents an attendee registered for a specific event.

    Ensures that an attendee can only register for an event once
    using their email address.

    Attributes:
        event (Event): The event the attendee is registered for.
        name (str): The name of the attendee.
        email (str): The email of the attendee.
        created_at (datetime): The timestamp when the attendee was created.
        updated_at (datetime): The timestamp when the attendee was last updated.
    """
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='attendees')
    name = models.CharField(max_length=255)
    email = models.EmailField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        """Meta options for the Attendee model."""
        unique_together = ('event', 'email')  # prevents duplicate registrations

    def __str__(self):
        """Returns a string representation of the attendee."""
        return f"Attendee-{str(self.id).zfill(6)}-{self.name}-{self.event.name}"