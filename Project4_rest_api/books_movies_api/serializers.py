from rest_framework import serializers
from django.contrib.contenttypes.models import ContentType
from django_comments_xtd.models import XtdComment

from .models import Book, Movie


class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'date', 'budget', 'actors']


class BookSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True, allow_null=True
    )

    class Meta:
        model = Book
        fields = ['id', 'title', 'date', 'category', 'movie', 'movie_id']


class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(source='submit_date', read_only=True)
    content = serializers.CharField(source='comment')
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(), write_only=True
    )
    object_pk = serializers.CharField(write_only=True)

    class Meta:
        model = XtdComment
        fields = [
            'id', 'user', 'user_name', 'content', 'created_at',
            'is_public', 'is_removed', 'site',
            'content_type', 'object_pk',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'is_public', 'is_removed', 'site']


class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']
