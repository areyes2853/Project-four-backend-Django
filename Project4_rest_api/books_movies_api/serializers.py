from rest_framework import serializers
from .models import Book, Movie
from django_comments.models import Comment

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

