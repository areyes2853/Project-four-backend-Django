# books_movies_api/views.py

from django.conf import settings
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

from rest_framework import generics, viewsets, status
from rest_framework.decorators import action, api_view
from rest_framework.response import Response

from django_comments_xtd.models import XtdComment
from django_comments_xtd.utils import get_user_avatar

from .models import Book, Movie
from .serializers import BookSerializer, MovieSerializer, CommentSerializer


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


# ─── CommentViewSet using django-comments-xtd ──────────────────────────────────

class CommentViewSet(viewsets.ModelViewSet):
    """
    Handles comments tied to any model via object_pk, app_label and content_type_model.
    """
    queryset = XtdComment.objects.filter(is_public=True, is_removed=False).order_by('submit_date')
    serializer_class = CommentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        object_pk = self.request.query_params.get('object_pk')
        model = self.request.query_params.get('content_type_model')
        app = self.request.query_params.get('app_label')

        if object_pk and model and app:
            try:
                ct = ContentType.objects.get_by_natural_key(app, model)
                return qs.filter(object_pk=object_pk, content_type=ct)
            except ContentType.DoesNotExist:
                return qs.none()
        return qs.none()

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        data = serializer.validated_data
        object_pk = request.data.get('object_pk')
        model = request.data.get('content_type_model')
        app = request.data.get('app_label')

        if not object_pk or not model or not app:
            return Response(
                {"detail": "object_pk, content_type_model, and app_label are required."},
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
            'object_pk': object_pk,
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

        comment = serializer.save(**comment_kwargs)
        headers = self.get_success_headers(serializer.data)
        return Response(
            CommentSerializer(comment).data,
            status=status.HTTP_201_CREATED,
            headers=headers
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
        return Response({"detail": "Permission denied."}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['post'])
    def preview(self, request):
        """
        Generates HTML preview of a comment without saving it.
        Expects object_pk, app_label, content_type_model, and comment in request.data.
        """
        data = request.data
        object_pk = data.get('object_pk')
        model = data.get('content_type_model')
        app = data.get('app_label')

        if not object_pk or not model or not app:
            return Response(
                {"detail": "object_pk, content_type_model, and app_label are required."},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            ct = ContentType.objects.get_by_natural_key(app, model)
        except ContentType.DoesNotExist:
            return Response(
                {"detail": f"Invalid content type: {app}.{model}"},
                status=status.HTTP_400_BAD_REQUEST
            )

        temp_data = {
            'content_type': ct,
            'object_pk': object_pk,
            'site_id': settings.SITE_ID,
            'user_name': data.get('user_name', ''),
            'user_email': data.get('user_email', ''),
            'user_url': data.get('user_url', ''),
            'comment': data.get('comment', ''),
            'user': request.user if request.user.is_authenticated else None,
            'submit_date': timezone.now(),
        }

        try:
            temp = XtdComment(**temp_data)
            html = get_html_comment_xtd(temp)
            return Response({'html': html}, status=status.HTTP_200_OK)
        except Exception:
            return Response({"detail": "Error generating preview"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ─── Site-wide Comment Endpoints ───────────────────────────────────────────────

@api_view(['GET'])
def site_comments_view(request):
    """
    Returns all public, non-removed comments tied to the special 'site' object.
    """
    comments = XtdComment.objects.filter(
        object_pk='site',
        is_public=True,
        is_removed=False
    ).order_by('-submit_date')
    serializer = CommentSerializer(comments, many=True)
    return Response(serializer.data)


@api_view(['POST'])
def add_site_comment_view(request):
    """
    Creates a comment tied to 'site' rather than a specific model instance.
    """
    data = request.data.copy()
    data.update({
        'object_pk': 'site',
        'app_label': 'books_movies_api',
        'content_type_model': 'movie',  # dummy model
    })
    serializer = CommentSerializer(data=data)
    serializer.is_valid(raise_exception=True)

    try:
        ct = ContentType.objects.get_by_natural_key(
            data['app_label'], data['content_type_model']
        )
    except ContentType.DoesNotExist:
        return Response({"detail": "Invalid content type."},
                        status=status.HTTP_400_BAD_REQUEST)

    comment_kwargs = {
        'content_type': ct,
        'object_pk': 'site',
        'site_id': settings.SITE_ID,
        'user': request.user if request.user.is_authenticated else None,
        'user_name': (
            request.user.get_full_name() or request.user.username
        ) if request.user.is_authenticated else None,
        'user_email': request.user.email if request.user.is_authenticated else None,
        'user_url': '',
        'comment': serializer.validated_data.get('comment'),
    }

    comment = serializer.save(**comment_kwargs)
    return Response(CommentSerializer(comment).data,
                    status=status.HTTP_201_CREATED)
