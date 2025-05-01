
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('books_movies_api.urls')),
    path('comments/', include('django_comments_xtd.urls')),
]
