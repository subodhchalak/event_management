# python imports
from datetime import datetime
from django.utils.timezone import localtime
import pytz


# django imports
from rest_framework import serializers

# in app imports
from event.models import Event, Attendee


# ---------------------------------------------------------------------------- #
#                                EventSerializer                               #
# ---------------------------------------------------------------------------- #


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event
        fields = [
            'id',
            'name',
            'location',
            'start_time',
            'end_time',
            'max_capacity',
        ]
        read_only_fields = ['id']
    

    def validate_start_time(self, value):
        """
        Ensure start_time is in the future.
        """
        if value <= datetime.now(value.tzinfo):
            raise serializers.ValidationError("Start time must be in the future.")
        return value

    def validate(self, data):
        """
        Ensure end_time is after start_time.
        """
        start = data.get('start_time')
        end = data.get('end_time')

        if start and end and end <= start:
            raise serializers.ValidationError("End time must be after start time.")

        return data

# ---------------------------------------------------------------------------- #
#                              AttendeeSerializer                              #
# ---------------------------------------------------------------------------- #


class AttendeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Attendee
        fields = [
            'id',
            'name',
            'email',
        ]
        read_only_fields = ['id']
    

