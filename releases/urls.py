from django.urls import path
from . import views
from releases.views import homepage

urlpatterns = [
    path('', views.release_list, name='release_list'),
    path('tag/<str:tag>/', views.release_list, name='release_list_by_tag'),
    path('upload/', views.upload_release, name='upload_release'),
    path('', homepage, name='home'),
    path('releases/', include('releases.urls')),
    path('admin/', admin.site.urls),
]
