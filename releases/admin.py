# ─── ADD TO YOUR EXISTING releases/admin.py ──────────────────────────────────
# (or replace the whole file with this if you don't have one)

from django.contrib import admin
from .models import ReleasePost, Artist, Event, AffiliateLink, ChatMessage, ChatUsername, WallCanvas


@admin.register(ReleasePost)
class ReleasePostAdmin(admin.ModelAdmin):
    list_display = ['title', 'release_datetime']
    search_fields = ['title', 'tags']


@admin.register(Artist)
class ArtistAdmin(admin.ModelAdmin):
    list_display = ['name', 'hometown', 'genre', 'display_order']
    list_editable = ['display_order']
    search_fields = ['name']


@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['title', 'venue', 'event_date']
    search_fields = ['title', 'venue']


@admin.register(AffiliateLink)
class AffiliateLinkAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'url', 'display_order', 'is_active']
    list_editable = ['display_order', 'is_active', 'category']
    list_filter = ['category', 'is_active']
    search_fields = ['name', 'description']


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ['username', 'message', 'timestamp']
    list_filter = ['username']
    readonly_fields = ['timestamp']


@admin.register(ChatUsername)
class ChatUsernameAdmin(admin.ModelAdmin):
    list_display = ['username', 'created_at']
    readonly_fields = ['created_at']


@admin.register(WallCanvas)
class WallCanvasAdmin(admin.ModelAdmin):
    list_display = ['pk', 'updated_at']
    readonly_fields = ['updated_at']