from django.contrib import admin

# Register your models here.
from .models import Book, Movie
admin.site.register(Book)
admin.site.register(Movie)