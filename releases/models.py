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

    youtube_url = models.URLField(max_length=500, blank=True, null=True, help_text="YouTube video URL (optional — used instead of or alongside audio file)")
    tags = models.CharField(max_length=200, blank=True, null=True, help_text="Comma-separated tags (e.g. boom bap, chill, 209)")
    release_datetime = models.DateTimeField(default=timezone.now, blank=True, null=True)

    def __str__(self):
        return self.title


class Artist(models.Model):
    name = models.CharField(max_length=200, help_text="Artist name (required)")
    hometown = models.CharField(max_length=200, blank=True, null=True)
    genre = models.CharField(max_length=200, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    headshot = models.ImageField(
        upload_to='artist_headshots/',
        storage=MediaStorage(),
        blank=True,
        null=True
    )
    soundcloud_url = models.URLField(max_length=500, blank=True, null=True)
    linktree_url = models.URLField(max_length=500, blank=True, null=True)
    instagram_url = models.URLField(max_length=500, blank=True, null=True)
    spotify_url = models.URLField(max_length=500, blank=True, null=True)
    display_order = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    venue = models.CharField(max_length=200, blank=True, null=True)
    location = models.CharField(max_length=200, blank=True, null=True)
    event_date = models.DateTimeField(default=timezone.now)
    ticket_link = models.URLField(max_length=500, blank=True, null=True)
    flyer = models.ImageField(
        upload_to='event_flyers/',
        storage=MediaStorage(),
        blank=True,
        null=True
    )
    tags = models.CharField(max_length=300, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-event_date']

    def __str__(self):
        return f"{self.title} - {self.event_date.strftime('%B %d, %Y')}"


# ─── Links Page ───────────────────────────────────────────────────────────────

class AffiliateLink(models.Model):
    CATEGORY_CHOICES = [
        ('artist', 'Artist'),
        ('label', 'Label'),
        ('studio', 'Studio'),
        ('store', 'Store'),
        ('other', 'Other'),
    ]
    name = models.CharField(max_length=200, help_text="Display name for the link")
    url = models.URLField(max_length=500, help_text="Full URL including https://")
    description = models.CharField(max_length=300, blank=True, null=True, help_text="Short description (optional)")
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='other')
    display_order = models.IntegerField(default=0, help_text="Lower numbers appear first")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['display_order', 'name']

    def __str__(self):
        return self.name


# ─── The Wall: Chat ───────────────────────────────────────────────────────────

class ChatUsername(models.Model):
    """Tracks reserved usernames and their password hashes."""
    username = models.CharField(max_length=50, unique=True)
    password_hash = models.CharField(max_length=128, help_text="bcrypt hash of the password")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.username


class ChatMessage(models.Model):
    username = models.CharField(max_length=50)
    message = models.TextField(max_length=500)
    timestamp = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['timestamp']

    def __str__(self):
        return f"[{self.timestamp.strftime('%H:%M')}] {self.username}: {self.message[:40]}"


# ─── The Wall: Canvas ─────────────────────────────────────────────────────────

class WallCanvas(models.Model):
    """
    Stores the entire canvas as a JSON blob of pixel data.
    Only one row ever exists (singleton pattern).
    """
    canvas_data = models.TextField(default='{}', help_text="JSON: { 'x,y': '#rrggbb', ... }")
    updated_at = models.DateTimeField(auto_now=True)

    @classmethod
    def get_instance(cls):
        obj, _ = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self):
        return f"Wall Canvas (last updated {self.updated_at})"