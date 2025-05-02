from django.db import models

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

