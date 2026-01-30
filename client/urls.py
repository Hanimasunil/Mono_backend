from django.urls import path
from . import views

urlpatterns = [
    # Admin views
    path('admin/', views.client_list, name='client_list'),
    path('admin/add/', views.client_add, name='client_add'),
    path('admin/<uuid:pk>/edit/', views.client_edit, name='client_edit'),
    path('admin/<uuid:pk>/view/', views.client_view, name='client_view'),
    path('admin/<uuid:pk>/delete/', views.client_delete, name='client_delete'),
    
    # Public views
    path('', views.client_list, name='client_list_public'),
    
    # API endpoints
    path('api/clients/', views.api_client_list, name='api_client_list'),
    path('api/clients/create/', views.api_client_create, name='api_client_create'),
    path('api/clients/<uuid:pk>/', views.api_client_detail, name='api_client_detail'),
    path('api/clients/<uuid:pk>/update/', views.api_client_update, name='api_client_update'),
    path('api/clients/<uuid:pk>/delete/', views.api_client_delete, name='api_client_delete'),
]