from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0004_releasepost_youtube_url'),
    ]

    operations = [
        migrations.AddField(
            model_name='releasepost',
            name='slug',
            field=models.SlugField(blank=True, max_length=120, unique=True),
        ),
    ]
