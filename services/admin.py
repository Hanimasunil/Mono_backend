from django.contrib import admin
from .models import Service, ServiceEnquiry

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    list_per_page = 20

@admin.register(ServiceEnquiry)
class ServiceEnquiryAdmin(admin.ModelAdmin):
    list_display = ['name', 'service', 'email', 'phone', 'created_at']
    list_filter = ['created_at', 'service']
    search_fields = ['name', 'email', 'phone', 'message']
    readonly_fields = ['created_at']
    list_per_page = 20