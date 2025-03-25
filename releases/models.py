from django.db import models
from django.utils import timezone
from .storage_backends import MediaStorage

class ReleasePost(models.Model):
    title = models.CharField(max_length=100)
    body = models.TextField(blank=True, null=True)



    album_art = models.ImageField(
        upload_to='album_art/',
        storage=MediaStorage(),
        blank=True,
        null=True
    )
    track_preview = models.FileField(
        upload_to='track_previews/',
        storage=MediaStorage(),
        blank=True,
        null=True
    )

    tags = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated tags (e.g. boom bap, chill, 209)")

    # Optional custom date
    release_datetime = models.DateTimeField(default=timezone.now, blank=True, null=True)

    def __str__(self):
        return self.title
