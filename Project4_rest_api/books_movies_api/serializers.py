from rest_framework import serializers
from .models import Book, Movie # Import Book and Movie models
from django_comments_xtd.models import XtdComment
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.models import ContentType # Ensure ContentType is imported

# --- Existing Serializers (keep these) ---
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

class ContentTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentType
        fields = ['id', 'app_label', 'model']


# --- Updated Comment Serializer ---
class CommentSerializer(serializers.ModelSerializer):
    # Read-only fields that represent the user and dates
    user = serializers.StringRelatedField(read_only=True)
    created_at = serializers.DateTimeField(source='submit_date', read_only=True)
    content = serializers.CharField(source='comment') # Maps input 'content' to model's 'comment'

    # Fields required to link the comment to an object (write_only for input)
    content_type = serializers.PrimaryKeyRelatedField(
        queryset=ContentType.objects.all(),
        write_only=True
    )
    object_pk = serializers.CharField(write_only=True)

    # --- New Field: To display the title of the commented object ---
    commented_object_title = serializers.SerializerMethodField()

    def get_commented_object_title(self, obj):
        """
        Looks up the actual commented object (Book or Movie) using content_type and object_pk
        and returns its title.
        """
        # obj.content_object automatically fetches the related object instance
        related_object = obj.content_object
        if related_object:
            # Check the type and return the title attribute
            # Assumes both Book and Movie models have a 'title' field
            if isinstance(related_object, (Book, Movie)):
                return related_object.title
            # Handle other potential model types if necessary, or return a default
            return str(related_object) # Fallback to string representation
        return None # Or "Unknown Object"


    class Meta:
        model = XtdComment
        fields = [
            'id', 'user', 'user_name', 'content', 'created_at',
            'is_public', 'is_removed', 'site', 'comment',
            'content_type', 'object_pk',
            'commented_object_title', # <-- Include the new field for output
            # Include 'parent' here if your XtdComment model has it and you want threaded comments
        ]
        read_only_fields = ['id', 'user', 'created_at', 'is_public', 'is_removed', 'site', 'commented_object_title'] # Make the new field read-only