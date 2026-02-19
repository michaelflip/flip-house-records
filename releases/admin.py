from django.contrib import admin
from .models import ReleasePost, Artist, Event

@admin.register(ReleasePost)
class ReleasePostAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_datetime']
    list_filter = ['release_datetime']
    search_fields = ['title', 'tags']

@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'hometown', 'genre', 'display_order']
    list_editable = ['display_order']
    search_fields = ['name', 'hometown', 'genre']
    list_filter = ['genre']
    ordering = ['display_order', 'name']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'hometown', 'genre')
        }),
        ('Biography', {
            'fields': ('bio',)
        }),
        ('Images', {
            'fields': ('headshot',)
        }),
        ('Links', {
            'fields': ('soundcloud_url', 'spotify_url', 'instagram_url', 'linktree_url')
        }),
        ('Display Settings', {
            'fields': ('display_order',)
        }),
    )


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'event_date', 'venue', 'location']
    list_filter = ['event_date']
    search_fields = ['title', 'venue', 'location', 'tags']
    ordering = ['-event_date']

    fieldsets = (
        ('Event Details', {
            'fields': ('title', 'description', 'event_date')
        }),
        ('Venue', {
            'fields': ('venue', 'location')
        }),
        ('Media', {
            'fields': ('flyer',)
        }),
        ('Links & Tags', {
            'fields': ('ticket_link', 'tags')
        }),
    )