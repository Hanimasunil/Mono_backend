from django.urls import path
from . import views

urlpatterns = [
    # Admin views - must come before public views to avoid slug collision
    path('admin/', views.admin_blog_list, name='admin_blog_list'),
    path('admin/add/', views.admin_blog_add, name='admin_blog_add'),
    path('admin/<uuid:pk>/edit/', views.admin_blog_edit, name='admin_blog_edit'),
    path('admin/<uuid:pk>/delete/', views.admin_blog_delete, name='admin_blog_delete'),
    
    # Public views
    path('', views.blog_list, name='blog_list'),
    path('<slug:slug>/', views.blog_detail, name='blog_detail'),
    path('preview/<slug:slug>/', views.blog_preview, name='blog_preview'),
    
    # API endpoints
    path('api/blog/', views.api_blog_list, name='api_blog_list'),
    path('api/blog/<slug:slug>/', views.api_blog_detail, name='api_blog_detail'),

]