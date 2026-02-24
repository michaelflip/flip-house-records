from django.urls import path
from . import views

urlpatterns = [
    path('', views.release_list, name='release_list'),
    path('tag/<str:tag>/', views.release_list, name='release_list_by_tag'),
    
    # Wall API Endpoints
    path('api/profile/update/', views.update_profile, name='update_profile'),
    path('api/profile/<str:username>/', views.get_profile, name='get_profile'),
    
    path('<slug:slug>/', views.release_detail, name='release_detail'),
]