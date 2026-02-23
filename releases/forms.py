from django import forms
from .models import ReleasePost

class ReleaseUploadForm(forms.ModelForm):
    class Meta:
        model = ReleasePost
        fields = ['title', 'body', 'album_art', 'track_preview', 'youtube_url', 'tags', 'release_datetime']
