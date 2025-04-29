from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('books_movies_api', '0002_remove_book_ismovie_remove_movie_isbook_book_movie'),
    ]

    operations = [
        # Step 1: Remove the old date field (it's a DateField)
        migrations.RemoveField(
            model_name='Book',
            name='date',
        ),
        migrations.RemoveField(
            model_name='Movie',
            name='date',
        ),
        # Step 2: Add a new date field as an IntegerField
        migrations.AddField(
            model_name='Book',
            name='date',
            field=models.IntegerField(),
        ),
        migrations.AddField(
            model_name='Movie',
            name='date',
            field=models.IntegerField(),
        ),
    ]
