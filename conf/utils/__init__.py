
from typing import Any
from rest_framework import pagination

__all__ = 'PaginatorGenerator',

class PaginatorGenerator:
    def __call__(self, _page_size:int=10, _paginator_class:Any=pagination.PageNumberPagination):
        
        class PaginatorClass(_paginator_class):
            page_size = _page_size
        
        return PaginatorClass
