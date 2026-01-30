from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from .models import Service, ServiceEnquiry
from .serializers import ServiceSerializer, ServiceEnquirySerializer
import json
import os

# Admin Views
@login_required(login_url='dashboard:admin_login')
def service_list_admin(request):
    """Admin service list view"""
    services = Service.objects.all().order_by('name')
    context = {
        'services': services,
        'page_title': 'Service Management',
        'page_subtitle': 'Manage services',
        'current_page': 'services'
    }
    return render(request, 'services/list.html', context)

@login_required(login_url='dashboard:admin_login')
def service_add(request):
    """Add new service"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        is_active = 'is_active' in request.POST
        
        service = Service.objects.create(
            name=name,
            description=description,
            is_active=is_active
        )
        
        # Handle icon upload
        if 'icon' in request.FILES:
            service.icon = request.FILES['icon']
            service.save()
        
        return redirect('dashboard:service_list_admin')
    
    context = {
        'page_title': 'Add Service',
        'page_subtitle': 'Create new service',
        'current_page': 'services'
    }
    return render(request, 'services/add.html', context)


@login_required(login_url='dashboard:admin_login')
def service_view(request, pk):
    """View service details"""
    service = get_object_or_404(Service, pk=pk)
    
    context = {
        'service': service,
        'page_title': f'View {service.name}',
        'page_subtitle': 'Service details',
        'current_page': 'services'
    }
    return render(request, 'services/view.html', context)


@login_required(login_url='dashboard:admin_login')
def service_edit(request, pk):
    """Edit service"""
    service = get_object_or_404(Service, pk=pk)
    
    if request.method == 'POST':
        service.name = request.POST.get('name', service.name)
        service.description = request.POST.get('description', service.description)
        # Checkbox handling - if not present, it means unchecked
        service.is_active = 'is_active' in request.POST
        

        
        # Handle icon upload
        if 'icon' in request.FILES:
            service.icon = request.FILES['icon']
        
        service.save()
        
        return redirect('dashboard:service_list_admin')
    
    context = {
        'service': service,
        'page_title': f'Edit {service.name}',
        'page_subtitle': 'Update service details',
        'current_page': 'services'
    }
    return render(request, 'services/add.html', context)


@login_required(login_url='dashboard:admin_login')
def service_delete(request, pk):
    """Delete service"""
    service = get_object_or_404(Service, pk=pk)
    
    if request.method == 'POST':
        service_name = service.name
        service.delete()
        return redirect('dashboard:service_list_admin')
    
    context = {
        'service': service,
        'page_title': f'Delete {service.name}',
        'page_subtitle': 'Confirm deletion',
        'current_page': 'services'
    }
    return render(request, 'services/delete.html', context)


# Public Views
def service_list(request):
    """Public service list view"""
    services = Service.objects.filter(is_active=True).order_by('name')
    context = {
        'services': services,
        'page_title': 'Our Services',
        'page_subtitle': 'What we offer'
    }
    return render(request, 'services/list.html', context)

def service_detail(request, slug):
    """Public service detail view"""
    service = get_object_or_404(Service, slug=slug, is_active=True)
    context = {
        'service': service,
        'page_title': service.name,
        'page_subtitle': 'Service Details'
    }
    return render(request, 'services/view.html', context)

# API Views
@csrf_exempt
def api_service_list(request):
    """GET service list"""
    if request.method == 'GET':
        services = Service.objects.filter(is_active=True).order_by('name')
        service_data = []
        
        for service in services:
            service_data.append({
                'id': str(service.id),
                'name': service.name,
                'slug': service.slug,
                'description': service.description,
                'icon': service.icon.url if service.icon else None,
                'created_at': service.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'data': service_data,
            'count': len(service_data)
        })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


# Service Enquiry Admin Views
@login_required(login_url='dashboard:admin_login')
def service_enquiry_list(request):
    """Admin service enquiry list view"""
    enquiries = ServiceEnquiry.objects.select_related('service').all().order_by('-created_at')
    context = {
        'enquiries': enquiries,
        'page_title': 'Service Enquiries',
        'page_subtitle': 'Manage service enquiries',
        'current_page': 'service_enquiries'
    }
    return render(request, 'services/enquiry_list.html', context)

@login_required(login_url='dashboard:admin_login')
def service_enquiry_view(request, pk):
    """View service enquiry details"""
    enquiry = get_object_or_404(ServiceEnquiry, pk=pk)
    
    context = {
        'enquiry': enquiry,
        'page_title': f'Enquiry from {enquiry.name}',
        'page_subtitle': 'Service enquiry details',
        'current_page': 'service_enquiries'
    }
    return render(request, 'services/enquiry_view.html', context)

@login_required(login_url='dashboard:admin_login')
def service_enquiry_delete(request, pk):
    """Delete service enquiry"""
    enquiry = get_object_or_404(ServiceEnquiry, pk=pk)
    
    if request.method == 'POST':
        enquiry_name = enquiry.name
        enquiry.delete()
        return redirect('service_enquiry_list')
    
    context = {
        'enquiry': enquiry,
        'page_title': f'Delete Enquiry from {enquiry.name}',
        'page_subtitle': 'Confirm deletion',
        'current_page': 'service_enquiries'
    }
    return render(request, 'services/enquiry_delete.html', context)


# Public Service Enquiry Form
def service_enquiry_create(request, service_id):
    """Create service enquiry from public form"""
    service = get_object_or_404(Service, id=service_id, is_active=True)
    
    if request.method == 'POST':
        name = request.POST.get('name')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        message = request.POST.get('message')
        
        if name and email and phone and message:
            ServiceEnquiry.objects.create(
                service=service,
                name=name,
                email=email,
                phone=phone,
                message=message
            )
            return JsonResponse({
                'success': True,
                'message': 'Thank you for your enquiry. We will contact you soon.'
            })
        else:
            return JsonResponse({
                'success': False,
                'error': 'All fields are required.'
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


# API for Service Enquiries
@csrf_exempt
@login_required(login_url='dashboard:admin_login')
def api_service_enquiry_list(request):
    """GET service enquiry list"""
    if request.method == 'GET':
        enquiries = ServiceEnquiry.objects.select_related('service').all().order_by('-created_at')
        enquiry_data = []
        
        for enquiry in enquiries:
            enquiry_data.append({
                'id': str(enquiry.id),
                'service_name': enquiry.service.name,
                'service_id': str(enquiry.service.id),
                'name': enquiry.name,
                'email': enquiry.email,
                'phone': enquiry.phone,
                'message': enquiry.message,
                'created_at': enquiry.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'data': enquiry_data,
            'count': len(enquiry_data)
        })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required(login_url='dashboard:admin_login')
def api_service_enquiry_detail(request, pk):
    """GET service enquiry detail"""
    if request.method == 'GET':
        try:
            enquiry = get_object_or_404(ServiceEnquiry, pk=pk)
            
            enquiry_data = {
                'id': str(enquiry.id),
                'service_name': enquiry.service.name,
                'service_id': str(enquiry.service.id),
                'name': enquiry.name,
                'email': enquiry.email,
                'phone': enquiry.phone,
                'message': enquiry.message,
                'created_at': enquiry.created_at.isoformat()
            }
            
            return JsonResponse({
                'success': True,
                'data': enquiry_data
            })
        except ServiceEnquiry.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Enquiry not found'
            }, status=404)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
@login_required(login_url='dashboard:admin_login')
def api_service_enquiry_delete(request, pk):
    """DELETE service enquiry"""
    if request.method == 'DELETE':
        try:
            enquiry = get_object_or_404(ServiceEnquiry, pk=pk)
            enquiry.delete()
            return JsonResponse({
                'success': True,
                'message': 'Enquiry deleted successfully'
            })
        except ServiceEnquiry.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Enquiry not found'
            }, status=404)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_service_detail(request, slug):
    """GET service detail (slug based)"""
    if request.method == 'GET':
        try:
            service = get_object_or_404(Service, slug=slug, is_active=True)
            
            service_data = {
                'id': str(service.id),
                'name': service.name,
                'slug': service.slug,
                'description': service.description,
                'icon': service.icon.url if service.icon else None,
                'is_active': service.is_active,
                'created_at': service.created_at.isoformat(),
                'updated_at': service.updated_at.isoformat()
            }
            
            return JsonResponse({
                'success': True,
                'data': service_data
            })
        except Service.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Service not found'
            }, status=404)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_service_create(request):
    """POST to create service"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            serializer = ServiceSerializer(data=data)
            if serializer.is_valid():
                service = serializer.save()
                return JsonResponse({
                    'success': True,
                    'data': ServiceSerializer(service).data,
                    'message': 'Service created successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': serializer.errors
                }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_service_update(request, slug):
    """PUT to update service"""
    if request.method == 'PUT':
        try:
            service = get_object_or_404(Service, slug=slug)
            data = json.loads(request.body)
            serializer = ServiceSerializer(service, data=data, partial=True)
            if serializer.is_valid():
                service = serializer.save()
                return JsonResponse({
                    'success': True,
                    'data': ServiceSerializer(service).data,
                    'message': 'Service updated successfully'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'error': serializer.errors
                }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_service_delete(request, slug):
    """DELETE to remove service"""
    if request.method == 'DELETE':
        try:
            service = get_object_or_404(Service, slug=slug)
            service.delete()
            return JsonResponse({
                'success': True,
                'message': 'Service deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)