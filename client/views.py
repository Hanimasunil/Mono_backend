from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Client
from .serializers import ClientSerializer


@login_required(login_url='dashboard:admin_login')
def client_list(request):
    """List all clients"""
    clients = Client.objects.all().order_by('-created_at')
    context = {
        'clients': clients,
        'page_title': 'Clients',
        'page_subtitle': 'Manage client listings',
        'current_page': 'clients',
    }
    return render(request, 'client/list.html', context)


@login_required(login_url='dashboard:admin_login')
def client_add(request):
    """Add a new client"""
    if request.method == 'POST':
        name = request.POST.get('name')
        website = request.POST.get('website', '')
        is_active = request.POST.get('is_active') == 'on'
        
        # Handle logo upload
        logo = request.FILES.get('logo')
        
        client = Client.objects.create(
            name=name,
            website=website,
            logo=logo,
            is_active=is_active
        )
        
        messages.success(request, f'Client "{name}" has been added successfully.')
        return redirect('dashboard:client_list')
    
    context = {
        'page_title': 'Add Client',
        'page_subtitle': 'Register a new client',
        'current_page': 'clients',
    }
    return render(request, 'client/add.html', context)


@login_required(login_url='dashboard:admin_login')
def client_edit(request, pk):
    """Edit a client"""
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        client.name = request.POST.get('name')
        client.website = request.POST.get('website', '')
        client.is_active = request.POST.get('is_active') == 'on'
        
        # Handle logo upload
        if 'logo' in request.FILES:
            client.logo = request.FILES.get('logo')
        
        client.save()
        
        messages.success(request, f'Client "{client.name}" has been updated successfully.')
        return redirect('dashboard:client_list')
    
    context = {
        'client': client,
        'page_title': f'Edit {client.name}',
        'page_subtitle': 'Update client details',
        'current_page': 'clients',
    }
    return render(request, 'client/add.html', context)


@login_required(login_url='dashboard:admin_login')
def client_view(request, pk):
    """View client details"""
    client = get_object_or_404(Client, pk=pk)
    
    context = {
        'client': client,
        'page_title': f'View {client.name}',
        'page_subtitle': 'Client details',
        'current_page': 'clients',
    }
    return render(request, 'client/view.html', context)


@login_required(login_url='dashboard:admin_login')
def client_delete(request, pk):
    """Delete a client"""
    client = get_object_or_404(Client, pk=pk)
    
    if request.method == 'POST':
        client_name = client.name
        client.delete()
        messages.success(request, f'Client "{client_name}" has been deleted successfully.')
        return redirect('dashboard:client_list')
    
    context = {
        'client': client,
        'page_title': f'Delete {client.name}',
        'page_subtitle': 'Confirm deletion',
        'current_page': 'clients',
    }
    return render(request, 'client/delete.html', context)


# API Views
@csrf_exempt
def api_client_list(request):
    """GET client list"""
    if request.method == 'GET':
        clients = Client.objects.filter(is_active=True).order_by('-created_at')
        client_data = []
        
        for item in clients:
            client_data.append({
                'id': str(item.id),
                'name': item.name,
                'logo': item.logo.url if item.logo else None,
                'website': item.website,
                'is_active': item.is_active,
                'created_at': item.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'data': client_data,
            'count': len(client_data)
        })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_client_detail(request, pk):
    """GET client detail"""
    if request.method == 'GET':
        try:
            client = get_object_or_404(Client, pk=pk, is_active=True)
            
            client_data = {
                'id': str(client.id),
                'name': client.name,
                'logo': client.logo.url if client.logo else None,
                'website': client.website,
                'is_active': client.is_active,
                'created_at': client.created_at.isoformat()
            }
            
            return JsonResponse({
                'success': True,
                'data': client_data
            })
        except Client.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Client not found'
            }, status=404)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_client_create(request):
    """POST to create client"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            serializer = ClientSerializer(data=data)
            if serializer.is_valid():
                client = serializer.save()
                return JsonResponse({
                    'success': True,
                    'data': ClientSerializer(client).data,
                    'message': 'Client created successfully'
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
def api_client_update(request, pk):
    """PUT to update client"""
    if request.method == 'PUT':
        try:
            client = get_object_or_404(Client, pk=pk)
            data = json.loads(request.body)
            serializer = ClientSerializer(client, data=data, partial=True)
            if serializer.is_valid():
                client = serializer.save()
                return JsonResponse({
                    'success': True,
                    'data': ClientSerializer(client).data,
                    'message': 'Client updated successfully'
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
def api_client_delete(request, pk):
    """DELETE to remove client"""
    if request.method == 'DELETE':
        try:
            client = get_object_or_404(Client, pk=pk)
            client.delete()
            return JsonResponse({
                'success': True,
                'message': 'Client deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)