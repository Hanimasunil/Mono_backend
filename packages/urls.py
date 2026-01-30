from django.urls import path
from . import views

urlpatterns = [
    # Admin views
    path('admin/', views.package_list, name='package_list'),
    path('admin/add/', views.package_add, name='package_add'),
    path('admin/<uuid:pk>/edit/', views.package_edit, name='package_edit'),
    path('admin/<uuid:pk>/view/', views.package_view, name='package_view'),
    path('admin/<uuid:pk>/delete/', views.package_delete, name='package_delete'),
    
    # Public views
    path('', views.package_list, name='package_list_public'),
    
    # API endpoints
    path('api/packages/', views.api_package_list, name='api_package_list'),
    path('api/packages/create/', views.api_package_create, name='api_package_create'),
    path('api/packages/<uuid:pk>/', views.api_package_detail, name='api_package_detail'),
    path('api/packages/<uuid:pk>/update/', views.api_package_update, name='api_package_update'),
    path('api/packages/<uuid:pk>/delete/', views.api_package_delete, name='api_package_delete'),
]