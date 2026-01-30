from django.urls import path
from . import views

urlpatterns = [
    # Admin views
    path('admin/services/', views.service_list_admin, name='service_list_admin'),
    path('admin/services/add/', views.service_add, name='service_add'),
    path('admin/services/<uuid:pk>/edit/', views.service_edit, name='service_edit'),
    path('admin/services/<uuid:pk>/view/', views.service_view, name='service_view'),
    path('admin/services/<uuid:pk>/delete/', views.service_delete, name='service_delete'),
    
    # Service Enquiry admin views
    path('admin/service-enquiries/', views.service_enquiry_list, name='service_enquiry_list'),
    path('admin/service-enquiries/<uuid:pk>/view/', views.service_enquiry_view, name='service_enquiry_view'),
    path('admin/service-enquiries/<uuid:pk>/delete/', views.service_enquiry_delete, name='service_enquiry_delete'),
    
    # Public views
    path('services/', views.service_list, name='service_list'),
    path('services/<slug:slug>/', views.service_detail, name='service_detail'),
    
    # Public service enquiry
    path('services/<uuid:service_id>/enquire/', views.service_enquiry_create, name='service_enquiry_create'),
    
    # API endpoints
    path('api/services/', views.api_service_list, name='api_service_list'),
    path('api/services/create/', views.api_service_create, name='api_service_create'),
    path('api/services/<slug:slug>/', views.api_service_detail, name='api_service_detail'),
    path('api/services/<slug:slug>/update/', views.api_service_update, name='api_service_update'),
    path('api/services/<slug:slug>/delete/', views.api_service_delete, name='api_service_delete'),
    
    # API endpoints for service enquiries
    path('api/service-enquiries/', views.api_service_enquiry_list, name='api_service_enquiry_list'),
    path('api/service-enquiries/<uuid:pk>/', views.api_service_enquiry_detail, name='api_service_enquiry_detail'),
    path('api/service-enquiries/<uuid:pk>/delete/', views.api_service_enquiry_delete, name='api_service_enquiry_delete'),
]