from rest_framework import serializers
from .models import Book, Movie, Comment

# Serializer for Movie 
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'date', 'budget', 'actors']

# Serializer for Book (includes the related movie)
class BookSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'date', 'category', 'movie']

class CommentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['id', 'movie', 'user', 'content', 'created_at']