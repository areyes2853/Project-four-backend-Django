from rest_framework import serializers
from .models import Book, Movie
from django_comments_xtd.models import XtdComment

# Serializer for Movie 
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'date', 'budget', 'actors']

# Serializer for Book (includes the related movie)
class BookSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    # Have to add this because
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True, allow_null=True
    )
    class Meta:
        model = Book
        fields = ['id', 'title', 'date', 'category', 'movie', 'movie_id']

class CommentSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    content = serializers.CharField(source='comment')
    created_at = serializers.DateTimeField(source='submit_date', read_only=True)
    class Meta:
        model = XtdComment
        fields = [
            'id', 'user', 'user_name','content', 'created_at', 'is_public', 'is_removed',
            # Add xtd fields if needed, e.g., 'parent', 'thread_id', 'level'
            # 'parent' is ForeignKey, often serialized as ID or nested serializer
        ]
        read_only_fields = ['user', 'created_at', 'is_public', 'is_removed']