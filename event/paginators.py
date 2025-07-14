# django imports
from rest_framework.pagination import PageNumberPagination


# ---------------------------------------------------------------------------- #
#                         StandardResultsSetPagination                         #
# ---------------------------------------------------------------------------- #



class StandardResultsSetPagination(PageNumberPagination):
    """
    Custom pagination class for API responses.

    - Default page size is 10 items per page.
    - Clients can override the page size using the 'page_size' query parameter.
    - Maximum allowed page size is capped at 20 to prevent excessive data loads.

    Example:
        GET /events?page=2&page_size=15
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 20
