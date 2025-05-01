from django.urls import path
from .views import BookList, MovieList, BookDetails, MovieDetails, CommentListCreateView


urlpatterns = [
    path('books/', BookList.as_view()),
    path('books/<int:pk>', BookDetails.as_view() ),
    path('movies/', MovieList.as_view()),
    path('movies/<int:pk>', MovieDetails.as_view() ),
    path('api/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
]