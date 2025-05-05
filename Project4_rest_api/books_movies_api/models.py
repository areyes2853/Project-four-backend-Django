# books_movies_api/models.py

import os
import requests
from urllib.parse import quote_plus

from django.db import models
from django.core.files.base import ContentFile


class Movie(models.Model):
    title   = models.CharField(max_length=255)
    date    = models.IntegerField()
    budget  = models.DecimalField(max_digits=12, decimal_places=2)
    actors  = models.TextField()

    def __str__(self):
        return self.title


class Book(models.Model):
    title       = models.CharField(max_length=255)
    date        = models.IntegerField()
    category    = models.CharField(max_length=100)
    movie       = models.ForeignKey(
                     Movie,
                     on_delete=models.SET_NULL,
                     null=True,
                     blank=True
                 )
    # Will store the direct URL to the image we fetched
    remote_url  = models.URLField(
                     blank=True,
                     help_text="Internal: direct URL of the book cover image"
                 )
    # ImageField requires Pillow; files go to MEDIA_ROOT/covers/
    cover       = models.ImageField(
                     upload_to='covers/',
                     blank=True,
                     null=True
                 )

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        """
        On first save (when there's no cover but we have a title),
        fetch the thumbnail from Google Books, store its URL in
        remote_url, download the image, and save it into `cover`.
        """
        if not self.cover and self.title:
            # 1) Query Google Books for this title
            query_url = (
                'https://www.googleapis.com/books/v1/volumes'
                f'?q=intitle:{quote_plus(self.title)}'
            )
            try:
                resp = requests.get(query_url, timeout=10)
                resp.raise_for_status()
                data = resp.json()
                # 2) Extract the first thumbnail link, if any
                items = data.get('items')
                if items:
                    thumb = (
                        items[0]
                        .get('volumeInfo', {})
                        .get('imageLinks', {})
                        .get('thumbnail')
                    )
                    if thumb:
                        # a) Save the direct URL for reference
                        self.remote_url = thumb
                        # b) Download the image bytes
                        img_resp = requests.get(thumb, timeout=10)
                        img_resp.raise_for_status()
                        # c) Derive a sane filename
                        name = os.path.basename(thumb.split('?')[0])
                        # d) Write to our ImageField (no recursion)
                        self.cover.save(name, ContentFile(img_resp.content), save=False)
            except Exception as e:
                # Optional: log the exception
                # from django.conf import settings
                # import logging
                # logger = logging.getLogger(__name__)
                # logger.warning(f"Could not fetch cover for '{self.title}': {e}")
                pass

        # Finally, perform the real save (writes both model & file)
        super().save(*args, **kwargs)
