
# books_movies_api/admin.py

from django.contrib import admin
from django import forms

from .models import Book, Movie
from django_comments_xtd.models import XtdComment
from django_comments_xtd.admin import XtdCommentsAdmin


# Register your Book and Movie models
admin.site.register(Book)
admin.site.register(Movie)

# Custom form for XtdComment to make fields optional
class CustomXtdCommentForm(forms.ModelForm):
    class Meta:
        model = XtdComment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Make these fields optional in the admin
        self.fields['user'].required = False
        self.fields['user_name'].required = False
        self.fields['user_email'].required = False
        self.fields['user_url'].required = False
        # Uncomment to make other fields optional:
        # self.fields['object_pk'].required = False
        # self.fields['content_type'].required = False

# Custom admin class using the form
class CustomXtdCommentAdmin(XtdCommentsAdmin):
    form = CustomXtdCommentForm
    # You can also exclude fields entirely:
    # exclude = ('user', 'user_email', 'user_url')

# Unregister default XtdComment admin and register the custom one
admin.site.unregister(XtdComment)
admin.site.register(XtdComment, CustomXtdCommentAdmin)
