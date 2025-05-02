from rest_framework import serializers
from .models import Book, Movie
from django_comments_xtd.models import XtdComment
from django.contrib.contenttypes.models import ContentType # Make sure this is imported

# Serializer for Movie
class MovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'date', 'budget', 'actors']

# Serializer for Book (includes the related movie)
class BookSerializer(serializers.ModelSerializer):
    movie = MovieSerializer(read_only=True)
    movie_id = serializers.PrimaryKeyRelatedField(
        queryset=Movie.objects.all(), source='movie', write_only=True, allow_null=True
    )
    class Meta:
        model = Book
        fields = ['id', 'title', 'date', 'category', 'movie', 'movie_id']

# Serializer for XtdComment
class CommentSerializer(serializers.ModelSerializer):
    # Read-only fields that represent the user and dates
    # Note: 'user' StringRelatedField will show username/fullname for authenticated users
    user = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(source='submit_date', read_only=True)

    # Field for comment content - maps input 'content' to model's 'comment' field
    content = serializers.CharField(source='comment')

    # Fields required to link the comment to an object using ContentTypes
    # These fields are expected in the input data (write_only=True)
    # 'content_type' expects the ID of the ContentType object
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        write_only=True
    )
    # 'object_pk' expects the primary key (ID) of the specific object being commented on (as a string)
    object_pk = serializers.CharField(write_only=True)

    # Optionally include parent for threaded comments if your XtdComment model supports it
    # Based on the previous error, you might need to confirm its existence and version compatibility
    # If your model has a parent field, you'd uncomment this and add 'parent' to Meta.fields
    # parent = serializers.PrimaryKeyRelatedField(
    #     queryset=XtdComment.objects.all(),
    #     allow_null=True, # Allow top-level comments (parent is null)
    #     required=False, # Parent is not required for top-level comments
    #     write_only=True
    # )


    class Meta:
        model = XtdComment
        fields = [
            'id',
            'user',         # Read-only (StringRelatedField derived from user ForeignKey)
            'user_name',    # Writable for anonymous comments, model field
            'content',      # Writable (maps input 'content' to model's 'comment')
            'created_at',   # Read-only (DateTimeField)
            'is_public',    # Model field
            'is_removed',   # Model field
            'site',         # Model field
            'comment',      # Model field (included if 'content' is source mapped, sometimes useful for output)
            'content_type', # Writable (PrimaryKeyRelatedField)
            'object_pk',    # Writable (CharField)
            # 'parent', # <-- Add this back if your XtdComment model has a 'parent' field for threading
        ]
        # Fields that should only be included when retrieving, not required for creation/update
        read_only_fields = ['id', 'user', 'created_at', 'is_public', 'is_removed', 'site'] # 'id' is always read-only


# --- Correction: Move ContentTypeSerializer outside CommentSerializer ---

# Serializer for ContentType - used for listing available content types
class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']