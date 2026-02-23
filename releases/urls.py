from django.urls import path
from . import views

urlpatterns = [
    path('', views.release_list, name='release_list'),
    path('tag/<str:tag>/', views.release_list, name='release_list_by_tag'),
    path('<slug:slug>/', views.release_detail, name='release_detail'),
]
