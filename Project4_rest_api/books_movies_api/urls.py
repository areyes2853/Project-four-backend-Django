from django.urls import path
from .views import BookList, MovieList, BookDetails, MovieDetails

urlpatterns = [
    path('books/', BookList.as_view()),
    path('books/<int:pk>', BookDetails.as_view() ),
    path('movies/', MovieList.as_view()),
    path('movies/<int:pk>', MovieDetails.as_view() ),
]