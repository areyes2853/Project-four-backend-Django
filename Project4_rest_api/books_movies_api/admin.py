from django.contrib import admin
from django_comments_xtd.models import XtdComment


# Register your models here.
from .models import Book, Movie
admin.site.register(Book)
admin.site.register(Movie)