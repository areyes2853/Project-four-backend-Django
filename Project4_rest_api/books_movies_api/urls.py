# books_movies_api/urls.py

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BookList, MovieList, BookDetails, MovieDetails, CommentViewSet

# Create a router and register our viewsets with it.
router = DefaultRouter()
# Register the CommentViewSet. It will handle paths starting with '/comments/' relative to where this router is included.
# Since this file is included at '/api/' in the project urls, these will become '/api/comments/' etc.
router.register(r'comments', CommentViewSet, basename='comment')

urlpatterns = [
    # Book URLs relative to /api/
    path('books/', BookList.as_view()),
    path('books/<int:pk>/', BookDetails.as_view() ),

    # Movie URLs relative to /api/
    path('movies/', MovieList.as_view()),
    path('movies/<int:pk>/', MovieDetails.as_view() ),

    # Include the router URLs at the ROOT level of THIS file's URL patterns.
    # When Project4_rest_api/urls.py includes this file at 'api/',
    # the router paths become:
    # /api/comments/
    # /api/comments/{id}/
    # /api/comments/preview/
    path('', include(router.urls)),

    # REMOVE THIS LINE: You do NOT want to include the library's default HTML-rendering URLs
    # path('comments/', include('django_comments_xtd.urls')),
]