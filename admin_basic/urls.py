from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [

    # ================= AUTH =================
    path('', views.admin_login, name='admin_login'),
    path('login/', views.admin_login, name='admin_login'),
    path('verify-otp/', views.verify_otp, name='verify_otp'),
    path('set-password/', views.set_password, name='set_password'),
    path('logout/', views.logout_view, name='logout'),

    # ================= DASHBOARD =================
    path('dashboard/', views.dashboard, name='dashboard'),

    # ================= TESTIMONIALS =================
    path(
        'testimonials/',
        views.TestimonialListView.as_view(),
        name='testimonials_list'
    ),
    path(
        'testimonials/add/',
        views.TestimonialCreateView.as_view(),
        name='testimonials_add'
    ),
    path(
        'testimonials/<uuid:pk>/edit/',
        views.TestimonialUpdateView.as_view(),
        name='testimonials_edit'
    ),
    path(
        'testimonials/<uuid:pk>/view/',
        views.TestimonialDetailView.as_view(),
        name='testimonials_view'
    ),
    path(
        'testimonials/<uuid:pk>/delete/',
        views.TestimonialDeleteView.as_view(),
        name='testimonials_delete'
    ),

    # ================= ENQUIRIES =================
    path(
        'enquiries/',
        views.EnquiryListView.as_view(),
        name='enquiries_list'
    ),
    path(
        'enquiries/add/',
        views.EnquiryCreateView.as_view(),
        name='enquiries_add'
    ),
    path(
        'enquiries/<uuid:pk>/edit/',
        views.EnquiryUpdateView.as_view(),
        name='enquiries_edit'
    ),
    path(
        'enquiries/<uuid:pk>/view/',
        views.EnquiryDetailView.as_view(),
        name='enquiries_view'
    ),
    path(
        'enquiries/<uuid:pk>/delete/',
        views.EnquiryDeleteView.as_view(),
        name='enquiries_delete'
    ),
    
    # ================= BLOG =================
    path('blog/', views.blog_list_admin, name='blog_list_admin'),
    path('blog/add/', views.blog_add, name='blog_add'),

    # ================= FORGOT PASSWORD =================
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password-verify/', views.reset_password_verify, name='reset_password_verify'),
    path('reset-password/', views.reset_password, name='reset_password'),
        
    # ================= PRODUCTS =================
    path('products/', views.product_list, name='product_list'),
    path('products/add/', views.product_add, name='product_add'),
    path('products/<slug:slug>/view/', views.product_view, name='product_view'),
    path('products/<slug:slug>/edit/', views.product_edit, name='product_edit'),
    path('products/<slug:slug>/delete/', views.product_delete, name='product_delete'),
    
    # ================= GALLERY =================
    path('gallery/', views.gallery_list, name='gallery_list'),
    path('gallery/add/', views.gallery_add, name='gallery_add'),
    path('gallery/<uuid:pk>/view/', views.gallery_view, name='gallery_view'),
    path('gallery/<uuid:pk>/edit/', views.gallery_edit, name='gallery_edit'),
    path('gallery/<uuid:pk>/delete/', views.gallery_delete, name='gallery_delete'),
    
    # ================= CLIENTS =================
    path('clients/', views.client_list, name='client_list'),
    path('clients/add/', views.client_add, name='client_add'),
    path('clients/<uuid:pk>/view/', views.client_view, name='client_view'),
    path('clients/<uuid:pk>/edit/', views.client_edit, name='client_edit'),
    path('clients/<uuid:pk>/delete/', views.client_delete, name='client_delete'),
    
    # ================= PACKAGES =================
    path('packages/', views.package_list, name='package_list'),
    path('packages/add/', views.package_add, name='package_add'),
    path('packages/<uuid:pk>/view/', views.package_view, name='package_view'),
    path('packages/<uuid:pk>/edit/', views.package_edit, name='package_edit'),
    path('packages/<uuid:pk>/delete/', views.package_delete, name='package_delete'),
    
    # ================= SERVICES =================
    path('services/', views.ServiceListView.as_view(), name='service_list_admin'),
    path('services/add/', views.ServiceCreateView.as_view(), name='service_add'),
    path('services/<uuid:pk>/view/', views.ServiceDetailView.as_view(), name='service_view'),
    path('services/<uuid:pk>/edit/', views.ServiceUpdateView.as_view(), name='service_edit'),
    path('services/<uuid:pk>/delete/', views.ServiceDeleteView.as_view(), name='service_delete'),
        
    # ================= API =================
    path('api/login/', views.api_admin_login),
    path('api/verify-otp/', views.api_verify_otp),
    path('api/set-password/', views.api_set_password),
    path('api/logout/', views.api_logout),
    path('api/dashboard/', views.api_dashboard_stats),

    # Testimonials API
    path('api/testimonials/', views.api_testimonial_list),
    path('api/testimonials/create/', views.api_testimonial_create),
    path('api/testimonials/<uuid:testimonial_id>/', views.api_testimonial_detail),
    path('api/testimonials/<uuid:testimonial_id>/update/', views.api_testimonial_update),
    path('api/testimonials/<uuid:testimonial_id>/delete/', views.api_testimonial_delete),

    # Enquiries API
    path('api/enquiries/', views.api_enquiry_list),
    path('api/enquiries/create/', views.api_enquiry_create),
    path('api/enquiries/<uuid:enquiry_id>/', views.api_enquiry_detail),
    path('api/enquiries/<uuid:enquiry_id>/update/', views.api_enquiry_update),
    path('api/enquiries/<uuid:enquiry_id>/delete/', views.api_enquiry_delete),
    path('api/enquiries/<uuid:enquiry_id>/mark-read/', views.api_enquiry_mark_read),
    # Product API
    path('api/products/', views.api_product_list),
    path('api/products/create/', views.api_product_create),
    path('api/products/<slug:slug>/', views.api_product_detail),
    path('api/products/<slug:slug>/update/', views.api_product_update),
    path('api/products/<slug:slug>/delete/', views.api_product_delete),
    #sERVICE api
    path('api/services/', views.api_service_list),
    path('api/services/create/', views.api_service_create),
    path('api/services/<slug:slug>/', views.api_service_detail),
    path('api/services/<slug:slug>/', views.api_service_detail),
    path('api/services/<slug:slug>/update/', views.api_service_update),
    path('api/services/<slug:slug>/delete/', views.api_service_delete),
    #Products api
    path('api/blogs/', views.api_blog_list_admin),
    path('api/blogs/create/', views.api_blog_create),
    path('api/blogs/<slug:slug>/', views.api_blog_detail_admin),
    path('api/blogs/<slug:slug>/update/', views.api_blog_update),
    path('api/blogs/<slug:slug>/delete/', views.api_blog_delete),
    
    # ================= GLOBAL SETTINGS =================
    path('settings/', views.global_settings, name='global_settings'),
    path('settings/add/', views.add_global_setting, name='add_global_setting'),
    path('settings/<uuid:pk>/update/', views.update_global_setting, name='update_global_setting'),
    path('settings/<uuid:pk>/delete/', views.delete_global_setting, name='delete_global_setting'),
]
