from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
class CustomPagination(PageNumberPagination):
    page_size = 6
    # Number of items per page
    page_size_query_param = 'page_size'  # Allow clients to set page size
    max_page_size = 100  # Maximum page size allowed
    page_query_param = 'p'

    def get_paginated_response(self, data):
        total_pages = self.page.paginator.num_pages
        return Response({
            'total_pages': total_pages,
            'count': self.page.paginator.count,
            'next': self.get_next_link(),
            'previous': self.get_previous_link(),
            'results': data,
        })