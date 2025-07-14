from datetime import datetime
from dateutil import parser
import pytz
from django.utils.timezone import make_aware, is_aware, is_naive

# ---------------------------------------------------------------------------- #
#                                localize_input                                #
# ---------------------------------------------------------------------------- #

def localize_input(data, timezone_str):
    tz = pytz.timezone(timezone_str)
    for key in ["start_time", "end_time"]:
        if key in data:
            dt = parser.parse(data[key])  # Parse string to datetime
            if dt.tzinfo is None:
                dt = tz.localize(dt)
            data[key] = dt.astimezone(pytz.UTC).isoformat()  # Make it UTC
    return data



# ---------------------------------------------------------------------------- #
#                            modify_datetime_format                            #
# ---------------------------------------------------------------------------- #

def modify_datetime_format(event_data, user_timezone, is_list=False):
    """
    Convert UTC datetime strings to the specified user timezone and format them.

    Args:
        event_data (dict or list of dict): Event or list of events with ISO datetime strings.
        user_timezone (str): e.g., 'Asia/Kolkata', 'America/New_York'.
        is_list (bool): True if event_data is a list of events.

    Returns:
        Modified event_data with formatted datetime fields.
    """
    # Load the user's timezone
    try:
        tz = pytz.timezone(user_timezone)
    except pytz.UnknownTimeZoneError:
        tz = pytz.UTC  # fallback to UTC

    def convert_datetime(iso_str):
        """Converts ISO 8601 UTC string to user's local time and formats it."""
        # Convert 'Z' to '+00:00' to make it ISO-compatible
        utc_dt = datetime.fromisoformat(iso_str.replace("Z", "+00:00"))
        utc_dt = utc_dt.replace(tzinfo=pytz.UTC)  # Make it timezone-aware
        local_dt = utc_dt.astimezone(tz)          # Convert to user's timezone
        return local_dt.strftime("%Y-%m-%d %H:%M:%S")

    if not is_list:
        event_data['start_time'] = convert_datetime(event_data['start_time'])
        event_data['end_time'] = convert_datetime(event_data['end_time'])
    else:
        for event in event_data:
            event['start_time'] = convert_datetime(event['start_time'])
            event['end_time'] = convert_datetime(event['end_time'])

    return event_data


# ---------------------------------------------------------------------------- #
#                                convert_to_utc                                #
# ---------------------------------------------------------------------------- #


def convert_to_utc(dt_value, user_timezone):
    """
    Converts a naive datetime from user's timezone to aware UTC datetime.
    """
    try:
        tz = pytz.timezone(user_timezone)

        # Step 1: Parse string to datetime if needed
        if isinstance(dt_value, str):
            if dt_value.endswith("Z"):
                dt_value = dt_value.replace("Z", "+00:00")
            try:
                dt_value = datetime.fromisoformat(dt_value)
            except ValueError:
                dt_value = datetime.strptime(dt_value, "%Y-%m-%d %H:%M:%S")

        # Step 2: Localize to user's timezone if it's naive
        if is_naive(dt_value):
            dt_value = tz.localize(dt_value)

        # Step 3: Convert to UTC
        return dt_value.astimezone(pytz.UTC)

    except Exception as e:
        raise ValueError(f"Invalid datetime or timezone: {e}")

