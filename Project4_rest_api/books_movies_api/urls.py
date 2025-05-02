# books_movies_api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    BookList, MovieList, BookDetails, MovieDetails,
    CommentViewSet, site_comments_view, add_site_comment_view
)

router = DefaultRouter()
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    # Book URLs
    path('books/', BookList.as_view()),
    path('books/<int:pk>/', BookDetails.as_view()),

    # Movie URLs
    path('movies/', MovieList.as_view()),
    path('movies/<int:pk>/', MovieDetails.as_view()),

    # API comment system (with model support)
    path('', include(router.urls)),

    # Site-wide comment (not model-specific)
    path('site-comments/', site_comments_view, name='site_comments'),
    path('site-comments/add/', add_site_comment_view, name='add_site_comment'),
]
