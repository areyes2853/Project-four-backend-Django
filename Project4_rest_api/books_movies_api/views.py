# books_movies_api/views.py

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from rest_framework import generics, viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from .models import Book, Movie
from .serializers import BookSerializer, MovieSerializer


# ─── Book Endpoints ────────────────────────────────────────────────────────────

class BookList(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


# ─── Movie Endpoints ────────────────────────────────────────────────────────────

class MovieList(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class MovieDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer
