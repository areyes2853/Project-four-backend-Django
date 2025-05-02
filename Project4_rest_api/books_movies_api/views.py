from django.shortcuts import render
from django.contrib.contenttypes.models import ContentType
from django.conf import settings
from django.utils import timezone

from rest_framework import generics, viewsets, status
from rest_framework.response import Response
from rest_framework.decorators import action

from django_comments_xtd.models import XtdComment
from django_comments_xtd.utils import get_user_avatar

from .models import Book, Movie
from .serializers import BookSerializer, MovieSerializer, CommentSerializer

class BookList(generics.ListCreateAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class BookDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Book.objects.all()
    serializer_class = BookSerializer

class MovieList(generics.ListCreateAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class MovieDetails(generics.RetrieveUpdateDestroyAPIView):
    queryset = Movie.objects.all()
    serializer_class = MovieSerializer

class CommentViewSet(viewsets.ModelViewSet):
    queryset = XtdComment.objects.filter(is_public=True, is_removed=False).order_by('submit_date')
    serializer_class = CommentSerializer

    def get_queryset(self):
        qs = super().get_queryset()
        object_pk = self.request.query_params.get('object_pk')
        content_type_model = self.request.query_params.get('content_type_model')
        app_label = self.request.query_params.get('app_label')

        if object_pk and content_type_model and app_label:
            try:
                content_type = ContentType.objects.get_by_natural_key(app_label, content_type_model)
                qs = qs.filter(object_pk=object_pk, content_type=content_type)
            except ContentType.DoesNotExist:
                qs = qs.none()
        else:
            qs = qs.none()

        return qs

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        object_pk = request.data.get('object_pk')
        content_type_model = request.data.get('content_type_model')
        app_label = request.data.get('app_label')

        if not object_pk or not content_type_model or not app_label:
            return Response({"detail": "object_pk, content_type_model, and app_label are required."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            content_type = ContentType.objects.get_by_natural_key(app_label, content_type_model)
        except ContentType.DoesNotExist:
            return Response({"detail": f"Invalid content type: {app_label}.{content_type_model}"}, status=status.HTTP_400_BAD_REQUEST)

        comment_data = serializer.validated_data
        comment_data['content_type'] = content_type
        comment_data['object_pk'] = object_pk
        comment_data['site_id'] = settings.SITE_ID

        if request.user.is_authenticated:
            comment_data['user'] = request.user
            comment_data['user_name'] = request.user.get_full_name() or request.user.get_username()
            comment_data['user_email'] = request.user.email
            comment_data['user_url'] = ''
        else:
            if not comment_data.get('user_name') or not comment_data.get('user_email'):
                return Response({"detail": "Name and Email are required for anonymous comments."}, status=status.HTTP_400_BAD_REQUEST)
            comment_data['user'] = None

        comment = serializer.save(**comment_data)

        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        if request.user.is_staff or (request.user == instance.user and (timezone.now() - instance.submit_date).seconds < settings.COMMENT_ALLOW_EDIT_SEC):
            instance.is_removed = True
            instance.save(update_fields=['is_removed'])
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            return Response({"detail": "You do not have permission to delete this comment."}, status=status.HTTP_403_FORBIDDEN)

    @action(detail=False, methods=['post'])
    def preview(self, request):
        return Response({"detail": "Preview functionality is not implemented."}, status=status.HTTP_501_NOT_IMPLEMENTED)
