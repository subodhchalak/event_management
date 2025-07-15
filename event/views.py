# python imports
from datetime import datetime

# django imports
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers


# in app imports
from event.utils import (
    localize_input,
    modify_datetime_format,
    convert_to_utc
)
from event.models import (
    Event,
    Attendee
)
from event.serializers import (
    EventSerializer,
    AttendeeSerializer,
)
from event.paginators import StandardResultsSetPagination



# ---------------------------------------------------------------------------- #
#                                AccountViewSet                                #
# ---------------------------------------------------------------------------- #

class EventModelViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing upcoming Event objects.

    Customizations:
    - Only allows GET, POST, and PUT HTTP methods.
    - Returns only events with a start_time in the future.
    - Uses StandardResultsSetPagination for paginated responses.

    Provided actions:
    - list: Retrieve a paginated list of upcoming events.
    - retrieve: Get details of a specific upcoming event.
    - create: Create a new event.
    - update: Fully update an existing upcoming event.
    - partial_update and destroy are disabled.
    """

    # Specifies the serializer class used to convert model instances to JSON and vice versa
    serializer_class = EventSerializer

    # Applies custom pagination with page size controls
    pagination_class = StandardResultsSetPagination

    # Restricts allowed HTTP methods to GET, POST, and PUT only
    http_method_names = ['get', 'post', 'put']

    # ------------------------------- get_queryset ------------------------------- #

    def get_queryset(self):
        """
        Returns only events whose start time is in the future.
        This ensures past events are excluded from the listing.
        """
        return Event.objects.filter(start_time__gte=datetime.now())
    
    # ----------------------------------- list ----------------------------------- #

    def list(self, request, *args, **kwargs):
        """
        Custom response with separate pagination and data sections.
        """
        queryset = self.filter_queryset(self.get_queryset())
        timezone_str = request.headers.get("X-Timezone", "UTC")
        
        # Apply pagination
        page = self.paginate_queryset(queryset)
        
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            # Copy the serialized data to modify the datetime formatting
            event_data = modify_datetime_format(event_data=serializer.data.copy(), user_timezone=timezone_str, is_list=True)
            count = self.paginator.page.paginator.count
            return Response(
                {
                    "success": True,
                    "message": "Upcoming events fetched successfully." if count > 0 else "No upcoming events found.",
                    "pagination": {
                        "count": self.paginator.page.paginator.count,
                        "next": self.paginator.get_next_link(),
                        "previous": self.paginator.get_previous_link()
                    },
                    "data": event_data
                },
                status=status.HTTP_200_OK
            )

        # If pagination is not used
        serializer = self.get_serializer(queryset, many=True)
        return Response({
                "success": True,
                "message": "Upcoming events fetched successfully.",
                "pagination": {},
                "data": serializer.data
            },
            status=status.HTTP_200_OK
        )


    # ---------------------------------- create ---------------------------------- #

    def create(self, request, *args, **kwargs):
        """
        Create a new event with a custom JSON response.

        Features:
        - Validates incoming data.
        - Handles serialization errors gracefully.
        - Returns `start_time` and `end_time` in a user-friendly format.
        """
        # Initialize the serializer with incoming request data
        # Convert datetime strings BEFORE serializer sees 
        timezone_str = request.headers.get("X-Timezone", "UTC")
        request_data = localize_input(request.data.copy(), timezone_str)
        serializer = self.get_serializer(data=request_data)
        

        try:
            # Validate the data; raise ValidationError if invalid
            serializer.is_valid(raise_exception=True)
            validated_data = serializer.validated_data

            # Convert to UTC based on user timezone
            validated_data["start_time"] = convert_to_utc(validated_data["start_time"], timezone_str)
            validated_data["end_time"] = convert_to_utc(validated_data["end_time"], timezone_str)

            # Create event
            event = Event.objects.create(**validated_data)
            event_serializer = self.get_serializer(event)

            # Format for user-friendly display
            event_data = modify_datetime_format(event_serializer.data.copy(), user_timezone=timezone_str)

            # Return success response with formatted data
            return Response(
                {
                    "success": True,
                    "message": "Event created successfully.",
                    "data": event_data,
                    "errors": []
                }, 
                status=status.HTTP_201_CREATED
            )

        except serializers.ValidationError:
            # If validation fails, return error response with detailed errors
            return Response(
                {
                    "success": False,
                    "message": "Failed to create event. Please correct the input data and try again.",
                    "errors": serializer.errors
                }, 
                status=status.HTTP_400_BAD_REQUEST
            )

        except Exception as e:
            # For any other unexpected errors
            return Response(
                {
                    "success": False,
                    "message": "An unexpected error occurred while creating the event.",
                    "errors": [str(e)]
                }, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    # --------------------------------- retrieve --------------------------------- #

    def retrieve(self, request, *args, **kwargs):
        """
        Retrieve the information of a specific event by ID.
        Returns a structured response with the event data if found.
        """
        try:
            # Get the event by primary key (id)
            event = Event.objects.get(id=kwargs['pk'])
            timezone_str = request.headers.get("X-Timezone", "UTC")
            
        except Event.DoesNotExist:
            return Response(
                {
                    "success": False,
                    "message": "Sorry, event not found. Please check the event ID and try again.",
                    "data": {},
                    "errors": []
                },
                status=status.HTTP_404_NOT_FOUND
            )

        # Serialize the event object
        serializer = EventSerializer(event)
        # Copy the serialized data to modify the datetime formatting
        event_data = modify_datetime_format(event_data=serializer.data.copy(), user_timezone=timezone_str, is_list=False)
        return Response(
            {
                "success": True,
                "message": "Event fetched successfully.",
                "data": event_data,
                "errors": []
            }, 
            status=status.HTTP_200_OK
        )
    
    # ---------------------------------- update ---------------------------------- #

    def update(self, request, *args, **kwargs):
        """
        Update an existing event with custom response and error handling.
        """
        try:
            timezone_str = request.headers.get("X-Timezone", "UTC")
            instance = self.get_object()
            serializer = self.get_serializer(instance, data=request.data)

            serializer.data["start_time"] = convert_to_utc(serializer.data["start_time"], timezone_str)
            serializer.data["end_time"] = convert_to_utc(serializer.data["end_time"], timezone_str)

            serializer.is_valid(raise_exception=True)
            self.perform_update(serializer)

            # Copy the serialized data to modify the datetime formatting
            event_data = modify_datetime_format(event_data=serializer.data.copy(), is_list=False)

            return Response({
                "success": True,
                "message": "Event updated successfully.",
                "data": event_data
            }, status=status.HTTP_200_OK)

        except serializers.ValidationError as e:
            return Response({
                "success": False,
                "message": "Validation failed during update.",
                "errors": [e.detail]
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                "success": False,
                "message": "An unexpected error occurred.",
                "errors": [str(e)]
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        

# ---------------------------------------------------------------------------- #
#                                  AttendeeMV                                  #
# ---------------------------------------------------------------------------- #


class AttendeeModelViewset(viewsets.ModelViewSet):
    """
    ViewSet for managing attendee registrations for a specific event.

    Features:
    - GET: Lists all attendees registered for the given event.
    - POST: Registers a new attendee if capacity allows and no duplicate email exists.
    - Pagination is applied using StandardResultsSetPagination.

    Restrictions:
    - Prevents overbooking beyond the event's max_capacity.
    - Prevents duplicate registrations using the same email.
    """

    # Serializer that converts Attendee objects to JSON and validates incoming data
    serializer_class = AttendeeSerializer

    # Applies custom pagination with page size controls
    pagination_class = StandardResultsSetPagination

    # ------------------------------- get_queryset ------------------------------- #

    def get_queryset(self):
        """
        Returns attendees for the event specified in the URL.
        Uses event_id from the URL kwargs to filter results.
        """
        queryset = Attendee.objects.filter(event=self.kwargs['event_id'])
        return queryset
    
    # ---------------------------------- create ---------------------------------- #

    def list(self, request, *args, **kwargs):
        """
        Returns a paginated list of attendees for a specific event.

        Custom Response Features:
        - Includes success flag and a descriptive message.
        - Returns pagination metadata (count, next, previous).
        - Handles empty attendee lists gracefully with appropriate messages.
        """

        # Filter attendees based on the event_id from the URL (handled by get_queryset)
        queryset = self.filter_queryset(self.get_queryset())

        # Apply pagination if it's enabled and supported
        page = self.paginate_queryset(queryset)
        if page is not None:
            # Serialize the paginated page
            serializer = self.get_serializer(page, many=True)

            # Total number of attendees for the event
            count = self.paginator.page.paginator.count

            # Return structured paginated response
            return Response({
                "success": True,
                "message": "Event attendees fetched successfully." if count > 0 else "No event attendees found.",
                "pagination": {
                    "count": count,
                    "next": self.paginator.get_next_link(),
                    "previous": self.paginator.get_previous_link()
                },
                "data": serializer.data
            }, status=status.HTTP_200_OK)

        # If pagination is not applied or there are no results
        serializer = self.get_serializer(queryset, many=True)
        return Response(
            {
                "success": True,
                "message": "Event attendees fetched successfully." if queryset.exists() else "No event attendees found.",
                "pagination": {},
                "data": serializer.data
            }, 
            status=status.HTTP_200_OK
        )


    # ---------------------------------- create ---------------------------------- #

    def create(self, request, *args, **kwargs):
        """
        Registers a new attendee for the given event.

        - Checks if the event exists.
        - Ensures the event has not reached its maximum capacity.
        - Validates and saves the attendee data.
        - Prevents duplicate registration for the same email.

        Returns:
        - 201 if registration is successful.
        - 400 if event is full or duplicate registration is attempted.
        """
        # Check if the event exists
        event = Event.objects.get(id=self.kwargs['event_id'])

        if event:
            # Check if event has reached maximum capacity
            if event.attendees.count() >= event.max_capacity:
                return Response(
                    {
                        'success': False,
                        'message': 'Sorry, event is full. New attendees can not be registered.',
                        'errors': []
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # Validate incoming attendee data
            serializer = self.get_serializer(data=request.data)
            if not serializer.is_valid():
                return Response(
                    {
                        'success': False,
                        'message': 'Incorrect data. Please check all the data fields and try again.',
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )


            serializer.is_valid(raise_exception=True)

            try:
                # Save attendee and associate with the event
                serializer.save(event=event)
            except Exception as e:
                # A unique constraint violation (duplicate email)
                return Response(
                    {
                        'success': False,
                        'message': "Attendee already registered for this event. Please try with the different email.",
                        'errors': serializer.errors
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

            # If successful, return 201 Created with success message and attendee data
            return Response(
                {
                    'success': True,
                    'message': "Attendee registered successfully!",
                    'data': serializer.data,
                    'errors': serializer.errors
                },
                status=status.HTTP_201_CREATED
            )
        else:
            # This block is actually unreachable — `get()` above would raise Event.DoesNotExist
            return Response(
                {
                    'success': False,
                    'message': "Event does not exist. Please check the input data and try again.",
                    'errors': serializer.errors
                },
                status=status.HTTP_400_BAD_REQUEST
            )
