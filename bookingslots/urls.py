from django.urls import path
from . import views

urlpatterns = [
    # Admin views
    path('admin/slots/', views.booking_slot_list, name='booking_slot_list'),
    path('admin/slots/add/', views.booking_slot_add, name='booking_slot_add'),
    path('admin/slots/<uuid:pk>/edit/', views.booking_slot_edit, name='booking_slot_edit'),
    
    path('admin/bookings/', views.booking_list, name='booking_list'),
    path('admin/bookings/<uuid:pk>/view/', views.booking_view, name='booking_view'),
    path('admin/bookings/<uuid:pk>/confirm/', views.booking_confirm, name='booking_confirm'),
    path('admin/bookings/<uuid:pk>/cancel/', views.booking_cancel, name='booking_cancel'),
    
    # Public views
    path('public/', views.booking_slot_public_list, name='booking_slot_public_list'),
    path('public/<uuid:slot_pk>/book/', views.booking_create, name='booking_create'),
    path('confirmation/<uuid:booking_id>/', views.booking_confirmation, name='booking_confirmation'),
    
    # API endpoints
    path('api/slots/', views.api_booking_slot_list, name='api_booking_slot_list'),
    path('api/slots/create/', views.api_booking_slot_create, name='api_booking_slot_create'),
    path('api/slots/<uuid:pk>/', views.api_booking_slot_detail, name='api_booking_slot_detail'),
    path('api/bookings/', views.api_booking_list, name='api_booking_list'),
    path('api/bookings/<uuid:pk>/', views.api_booking_detail, name='api_booking_detail'),
    path('api/bookings/create/', views.api_create_booking, name='api_create_booking'),
]