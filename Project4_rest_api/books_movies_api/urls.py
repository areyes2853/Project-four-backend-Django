# books_movies_api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter

from .views import (
    BookList, BookDetails,
    MovieList, MovieDetails,
    CommentViewSet
)

# Set up DRF router for comments
router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    # Book endpoints
    path('books/', BookList.as_view(), name='book-list'),
    path('books/<int:pk>/', BookDetails.as_view(), name='book-detail'),

    # Movie endpoints
    path('movies/', MovieList.as_view(), name='movie-list'),
    path('movies/<int:pk>/', MovieDetails.as_view(), name='movie-detail'),


    # Comment endpoints (via router)
    path('', include(router.urls)),
]
