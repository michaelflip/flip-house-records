from django.contrib import admin
from .models import ReleasePost

@admin.register(ReleasePost)
class ReleasePostAdmin(admin.ModelAdmin):
    list_display = ('title', 'release_datetime', 'tags')
    search_fields = ('title', 'tags')
    list_filter = ('release_datetime',)
