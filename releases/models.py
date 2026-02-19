from django.db import models
from django.utils import timezone
from fliphouserecords.storage_backends import MediaStorage

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


class Artist(models.Model):
    # Required field
    name = models.CharField(max_length=200, help_text="Artist name (required)")
    
    # Optional fields
    hometown = models.CharField(max_length=200, blank=True, null=True, help_text="Hometown/Location")
    genre = models.CharField(max_length=200, blank=True, null=True, help_text="Music genre")
    bio = models.TextField(blank=True, null=True, help_text="Artist biography")
    
    # Image field for headshot/display photo
    headshot = models.ImageField(
        upload_to='artist_headshots/',
        storage=MediaStorage(),
        blank=True,
        null=True,
        help_text="Artist headshot or display image"
    )
    
    # Optional social/music links
    soundcloud_url = models.URLField(max_length=500, blank=True, null=True, help_text="SoundCloud profile URL")
    linktree_url = models.URLField(max_length=500, blank=True, null=True, help_text="Linktree or other link URL")
    
    # Additional optional links
    instagram_url = models.URLField(max_length=500, blank=True, null=True, help_text="Instagram profile URL")
    spotify_url = models.URLField(max_length=500, blank=True, null=True, help_text="Spotify profile URL")
    
    # Order for display
    display_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200, help_text="Event name (required)")
    description = models.TextField(blank=True, null=True, help_text="Event description")
    venue = models.CharField(max_length=200, blank=True, null=True, help_text="Venue name")
    location = models.CharField(max_length=200, blank=True, null=True, help_text="City, State or full address")
    event_date = models.DateTimeField(default=timezone.now, help_text="Date and time of the event")
    ticket_link = models.URLField(max_length=500, blank=True, null=True, help_text="Link to buy tickets")
    flyer = models.ImageField(
        upload_to='event_flyers/',
        storage=MediaStorage(),
        blank=True,
        null=True,
        help_text="Event flyer image"
    )
    tags = models.CharField(max_length=300, blank=True, null=True, help_text="Comma-separated tags (e.g. hip hop, modesto, 209)")

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-event_date']

    def __str__(self):
        return f"{self.title} - {self.event_date.strftime('%B %d, %Y')}"