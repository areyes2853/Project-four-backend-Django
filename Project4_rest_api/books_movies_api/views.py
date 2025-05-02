# books_movies_api/views.py

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from rest_framework import generics, viewsets, status
from rest_framework.response import Response

from django_comments_xtd.models import XtdComment
from .models import Book, Movie
from .serializers import BookSerializer, MovieSerializer, CommentSerializer


# ─── Book Endpoints ────────────────────────────────────────────────────────────
class BookList(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


class BookDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer


# ─── Movie Endpoints ───────────────────────────────────────────────────────────
class MovieList(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


class MovieDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer


# ─── Comment Endpoints ─────────────────────────────────────────────────────────
class CommentViewSet(viewsets.ModelViewSet):
    """
    CRUD for threaded XtdComment, filtered by object_pk/app_label/content_type_model.
    """
    queryset = XtdComment.objects.filter(is_public=True, is_removed=False)\
                                 .order_by('submit_date')
    serializer_class = CommentSerializer

    def get_queryset(self):
        qs    = super().get_queryset()
        pk    = self.request.query_params.get('object_pk')
        model = self.request.query_params.get('content_type_model')
        app   = self.request.query_params.get('app_label')

        if pk and model and app:
            try:
                ct = ContentType.objects.get_by_natural_key(app, model)
                return qs.filter(object_pk=pk, content_type=ct)
            except ContentType.DoesNotExist:
                pass
        return qs.none()

    def create(self, request, *args, **kwargs):
        data  = request.data
        pk    = data.get('object_pk')
        model = data.get('content_type_model')
        app   = data.get('app_label')

        if not (pk and model and app):
            return Response(
                {"detail": "object_pk, content_type_model, and app_label required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ct = ContentType.objects.get_by_natural_key(app, model)
        except ContentType.DoesNotExist:
            return Response(
                {"detail": f"Invalid content type: {app}.{model}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        comment_kwargs = {
            'content_type': ct,
            'object_pk': pk,
            'site_id': settings.SITE_ID,
            'user': request.user if request.user.is_authenticated else None,
            'user_name': (
                request.user.get_full_name() or request.user.username
            ) if request.user.is_authenticated else data.get('user_name'),
            'user_email': (
                request.user.email
            ) if request.user.is_authenticated else data.get('user_email'),
            'user_url': '',
            'comment': data.get('comment'),
        }

        serializer = self.get_serializer(data=comment_kwargs)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()
        return Response(
            self.get_serializer(comment).data,
            status=status.HTTP_201_CREATED
        )

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        allowed = (
            request.user.is_staff
            or (
                request.user == instance.user
                and (timezone.now() - instance.submit_date).seconds
                    < getattr(settings, 'COMMENT_ALLOW_EDIT_SEC', 300)
            )
        )
        if allowed:
            instance.is_removed = True
            instance.save(update_fields=['is_removed'])
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response({"detail": "Permission denied."},
                        status=status.HTTP_403_FORBIDDEN)
