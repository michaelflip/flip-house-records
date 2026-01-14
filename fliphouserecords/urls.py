from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from releases.views import homepage, artists, contact, merch, events  

urlpatterns = [
    path('', homepage, name='home'),
    path('admin/', admin.site.urls),
    path('releases/', include('releases.urls')),
    path('artists/', artists, name='artists'),
    path('contact/', contact, name='contact'),
    path('merch/', merch, name='merch'),
    path('events/', events, name='events'),  
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)