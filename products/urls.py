from django.urls import path
from . import views

urlpatterns = [
    # Admin views - must come before public views to avoid slug collision
    path('admin/', views.product_list, name='product_list'),
    path('admin/add/', views.product_add, name='product_add'),
    path('admin/<slug:slug>/edit/', views.product_edit, name='product_edit'),
    path('admin/<slug:slug>/delete/', views.product_delete, name='product_delete'),
    
    # Public views
    path('', views.product_list, name='product_list_public'),
    path('<slug:slug>/', views.product_detail, name='product_detail'),
    
    # API endpoints
    path('api/products/', views.api_product_list, name='api_product_list'),
    path('api/products/<slug:slug>/', views.api_product_detail, name='api_product_detail'),

]