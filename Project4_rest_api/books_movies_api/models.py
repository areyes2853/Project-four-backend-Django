from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)
    date = models.IntegerField()
    category = models.CharField(max_length=100)
    movie = models.ForeignKey('Movie', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return self.title

class Movie(models.Model):
    title = models.CharField(max_length=255)
    date = models.IntegerField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    actors = models.TextField()
    
    def __str__(self):
        return self.title

class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f'Comment by {self.user.username} on {self.movie.title}'