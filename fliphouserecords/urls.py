from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from releases.views import homepage, artists, contact, merch, events, links, wall, password_reset_confirm, update_profile, get_profile

urlpatterns = [
    path('', homepage, name='home'),
    path('admin/', admin.site.urls),
    path('releases/', include('releases.urls')),
    path('artists/', artists, name='artists'),
    path('contact/', contact, name='contact'),
    path('merch/', merch, name='merch'),
    path('events/', events, name='events'),
    path('links/', links, name='links'),
    path('wall/', wall, name='wall'),
    path('wall/reset-password/<str:token>/', password_reset_confirm, name='password_reset_confirm'),
    
    # REMOVED the 'views.' prefix since we imported them directly above
    path('api/profile/update/', update_profile, name='update_profile'),
    path('api/profile/<str:username>/', get_profile, name='get_profile'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)