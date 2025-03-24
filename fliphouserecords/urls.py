from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from releases.views import homepage  # ✅ import your homepage view

urlpatterns = [
    path('', homepage, name='home'),  # ✅ this line routes the root URL to index.html
    path('admin/', admin.site.urls),
    path('releases/', include('releases.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
