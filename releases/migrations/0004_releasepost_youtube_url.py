from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('releases', '0003_affiliatelink_artist_chatmessage_chatusername_event_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='releasepost',
            name='youtube_url',
            field=models.URLField(blank=True, help_text='YouTube video URL (optional — used instead of or alongside audio file)', max_length=500, null=True),
        ),
    ]