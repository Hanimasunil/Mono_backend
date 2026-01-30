from django.urls import path
from . import views

urlpatterns = [
    # Admin views
    path('admin/', views.gallery_list, name='gallery_list'),
    path('admin/add/', views.gallery_add, name='gallery_add'),
    path('admin/<uuid:pk>/edit/', views.gallery_edit, name='gallery_edit'),
    path('admin/<uuid:pk>/view/', views.gallery_view, name='gallery_view'),
    path('admin/<uuid:pk>/delete/', views.gallery_delete, name='gallery_delete'),
    
    # Public views
    path('', views.gallery_list, name='gallery_list_public'),
    
    # API endpoints
    path('api/gallery/', views.api_gallery_list, name='api_gallery_list'),
    path('api/gallery/create/', views.api_gallery_create, name='api_gallery_create'),
    path('api/gallery/<uuid:pk>/', views.api_gallery_detail, name='api_gallery_detail'),
    path('api/gallery/<uuid:pk>/update/', views.api_gallery_update, name='api_gallery_update'),
    path('api/gallery/<uuid:pk>/delete/', views.api_gallery_delete, name='api_gallery_delete'),
]