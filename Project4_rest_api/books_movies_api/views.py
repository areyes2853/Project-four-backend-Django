from django.conf import settings
from django.contrib.contenttypes.models import ContentType # Need this import
from django.utils import timezone

from rest_framework import generics, viewsets, status
from rest_framework.response import Response
# Add filters backend for queryset filtering in ViewSet
from rest_framework.filters import SearchFilter, OrderingFilter
from django_filters.rest_framework import DjangoFilterBackend # If you use django-filter

from django_comments_xtd.models import XtdComment
from .models import Book, Movie
# Fix: Removed trailing comma in import statement and ensure ContentTypeSerializer is imported
from .serializers import (
    BookSerializer,
    MovieSerializer,
    CommentSerializer,
    ContentTypeSerializer, # Ensure ContentTypeSerializer is listed here
)


# ─── Book Endpoints (using Generic Views) ────────────────────────────────────
# Note: If you register these with a router like `router.register(r'books', BookList)`,
# it will NOT work. Router is for ViewSets. Keep these if you use path().
# Consider converting these to ViewSets if you want them handled by a router.
class BookList(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


# ─── Movie Endpoints (using Generic Views) ───────────────────────────────────
# Note: Same as Book endpoints, use path() for these if they are generic views.
# Consider converting these to ViewSets if you want them handled by a router.
class MovieList(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class MovieDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


# ─── Comment Endpoints (using ViewSet) ───────────────────────────────────────
class CommentViewSet(viewsets.ModelViewSet):
    """
    API for threaded XtdComment. Supports filtering by object_pk and content_type ID
    for list view. Handles comment creation details in the create method.
    """
    # Base queryset (can be filtered further in get_queryset)
    # Ensure filtering here matches what you want to show by default
    queryset = XtdComment.objects.filter(is_public=True, is_removed=False)\
                                 .order_by('thread_id', 'order') # Order for threading

    serializer_class = CommentSerializer

    # --- Filtering for List View ---
    # Allows filtering by query parameters like ?content_type=15&object_pk=5
    filter_backends = [DjangoFilterBackend, OrderingFilter, SearchFilter] # Add DjangoFilterBackend if using django-filter
    filterset_fields = ['object_pk', 'content_type'] # Enable filtering on these fields
    ordering_fields = ['submit_date'] # Allows sorting like ?order_by=-submit_date
    search_fields = ['comment', 'user_name', 'user_email'] # Allows searching like ?search=keyword

    # Note: The get_queryset method is no longer strictly needed if using filterset_fields,
    # as DjangoFilterBackend handles filtering automatically.
    # If you need more complex filtering logic, you can keep get_queryset
    # and apply filters manually, but using filterset_fields is the standard DRF way.
    # Let's keep the manual get_queryset for now as it uses get_by_natural_key which is useful
    # if you preferred app_label/model name in query params instead of content_type ID.
    # However, the frontend is sending content_type ID, so filterset_fields is better.
    # Let's simplify get_queryset to rely on standard filtering.
    #
    # def get_queryset(self):
    #     # This custom get_queryset is only needed if you want filtering
    #     # logic beyond simple field matching (like filtering by app_label/model name)
    #     # Since your frontend sends content_type ID, filterset_fields is sufficient
    #     # and recommended for standard filtering via query params.
    #     # Remove or simplify this if using filterset_fields.
    #     # Example using filterset_fields:
    #     qs = super().get_queryset()
    #     # Standard DRF filtering will be applied automatically via filterset_fields
    #     return qs


    # --- Custom Create Method ---
    # This method overrides the default ModelViewSet.create
    def create(self, request, *args, **kwargs):
        # Use the serializer to validate the input data including content_type,
        # object_pk, content (mapped to comment), and user_name.
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Manually set fields that come from the request context, not user input
        # The serializer's create method will merge validated_data with these extra args
        extra_kwargs = {
            'user': request.user if request.user.is_authenticated else None,
            'site_id': settings.SITE_ID,
            # XtdComment model has user_email and user_url, often derived for auth users
            'user_email': request.user.email if request.user.is_authenticated else '',
            'user_url': '', # Set user_url if applicable
            # 'user_name' is already in validated_data if provided by anonymous user
            # If authenticated user, you might override user_name here if you prefer
            # a specific display name even when 'user' field is set.
            # E.g., 'user_name': request.user.get_full_name() or request.user.username if request.user.is_authenticated else validated_data.get('user_name'),
        }

        # Save the comment using the serializer. This triggers the serializer's
        # create method with validated_data combined with extra_kwargs.
        comment = serializer.save(**extra_kwargs)

        # Return the response using the serializer to format the output
        return Response(
            self.get_serializer(comment).data,
            status=status.HTTP_201_CREATED
        )

    # --- Custom Destroy Method ---
    # This method overrides the default ModelViewSet.destroy
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        # Check if the user is staff or the comment author within the edit window
        allowed = (
            request.user.is_staff
            or (
                request.user.is_authenticated # Ensure user is logged in
                and request.user == instance.user
                and (timezone.now() - instance.submit_date).seconds
                    < getattr(settings, 'COMMENT_ALLOW_EDIT_SEC', 300)
            )
        )
        if allowed:
            # Soft delete the comment by setting is_removed to True
            instance.is_removed = True
            instance.save(update_fields=['is_removed'])
            return Response(status=status.HTTP_204_NO_CONTENT)

        # Return permission denied if not allowed
        return Response({"detail": "Permission denied."},
                        status=status.HTTP_403_FORBIDDEN)

# ─── ContentType Endpoints (using ViewSet) ───────────────────────────────────
class ContentTypeViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API to list available ContentTypes.
    """
    queryset = ContentType.objects.all()
    serializer_class = ContentTypeSerializer # This now correctly refers to the top-level serializer
    filter_backends = [OrderingFilter, SearchFilter]
    ordering_fields = ['app_label', 'model']
    search_fields = ['app_label', 'model']