from django.urls import path
from .views import BookList, MovieList

urlpatterns = [
    path('books/', BookList.as_view()),
    path('movies/', MovieList.as_view()),
]