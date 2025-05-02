# books_movies_api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookList, MovieList, BookDetails, MovieDetails
)

router = DefaultRouter()


urlpatterns = [
    # Book URLs
    path('books/', BookList.as_view()),
    path('books/<int:pk>/', BookDetails.as_view()),

    # Movie URLs
    path('movies/', MovieList.as_view()),
    path('movies/<int:pk>/', MovieDetails.as_view()),
]
