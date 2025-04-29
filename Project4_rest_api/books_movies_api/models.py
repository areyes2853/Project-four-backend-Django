from django.db import models

# Create your models here.
class Book(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    category = models.CharField(max_length=100)
    movie = models.ForeignKey('Movie', on_delete=models.SET_NULL, null=True, blank=True)


class Movie(models.Model):
    title = models.CharField(max_length=255)
    date = models.DateField()
    budget = models.DecimalField(max_digits=12, decimal_places=2)
    actors = models.TextField()
    