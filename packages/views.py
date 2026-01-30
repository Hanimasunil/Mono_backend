from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Package
from .serializers import PackageSerializer
import json


@login_required(login_url='dashboard:admin_login')
def package_list(request):
    """List all packages"""
    packages = Package.objects.all().order_by('name')
    context = {
        'packages': packages,
        'page_title': 'Packages',
        'page_subtitle': 'Manage package listings',
        'current_page': 'packages',
    }
    return render(request, 'packages/list.html', context)


@login_required(login_url='dashboard:admin_login')
def package_add(request):
    """Add a new package"""
    if request.method == 'POST':
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        features = request.POST.get('features', '[]')
        is_active = request.POST.get('is_active') == 'on'
        
        # Handle features JSON string
        try:
            features_list = json.loads(features) if features else []
        except json.JSONDecodeError:
            features_list = []
        
        package = Package.objects.create(
            name=name,
            description=description,
            price=price,
            features=json.dumps(features_list),  # Store as JSON string
            is_active=is_active
        )
        
        messages.success(request, f'Package "{name}" has been added successfully.')
        return redirect('dashboard:package_list')
    
    context = {
        'page_title': 'Add Package',
        'page_subtitle': 'Create a new package',
        'current_page': 'packages',
    }
    return render(request, 'packages/add.html', context)


@login_required(login_url='dashboard:admin_login')
def package_edit(request, pk):
    """Edit a package"""
    package = get_object_or_404(Package, pk=pk)
    
    if request.method == 'POST':
        package.name = request.POST.get('name')
        package.description = request.POST.get('description')
        package.price = request.POST.get('price')
        features = request.POST.get('features', '[]')
        package.is_active = request.POST.get('is_active') == 'on'
        
        # Handle features JSON string
        try:
            features_list = json.loads(features) if features else []
        except json.JSONDecodeError:
            features_list = []
        package.features = json.dumps(features_list)  # Store as JSON string
        
        package.save()
        
        messages.success(request, f'Package "{package.name}" has been updated successfully.')
        return redirect('dashboard:package_list')
    
    # Convert features to JSON string for the template
    features_json = json.dumps(package.features) if isinstance(package.features, list) else json.dumps([])

    context = {
        'package': package,
        'page_title': f'Edit {package.name}',
        'page_subtitle': 'Update package details',
        'features_json': features_json,
        'current_page': 'packages',
    }
    return render(request, 'packages/add.html', context)


@login_required(login_url='dashboard:admin_login')
def package_view(request, pk):
    """View package details"""
    package = get_object_or_404(Package, pk=pk)
    import json
    # Parse features from JSON string
    try:
        features_list = json.loads(package.features) if package.features else []
    except json.JSONDecodeError:
        features_list = []
    
    context = {
        'package': package,
        'packagefeatures': json.dumps(features_list),
        'page_title': f'View {package.name}',
        'page_subtitle': 'Package details',
        'current_page': 'packages',
    }
    return render(request, 'packages/view.html', context)


@login_required(login_url='dashboard:admin_login')
def package_delete(request, pk):
    """Delete a package"""
    package = get_object_or_404(Package, pk=pk)
    
    if request.method == 'POST':
        package_name = package.name
        package.delete()
        messages.success(request, f'Package "{package_name}" has been deleted successfully.')
        return redirect('dashboard:package_list')
    
    context = {
        'package': package,
        'page_title': f'Delete {package.name}',
        'page_subtitle': 'Confirm deletion',
        'current_page': 'packages',
    }
    return render(request, 'packages/delete.html', context)


# API Views
@csrf_exempt
def api_package_list(request):
    """GET package list"""
    if request.method == 'GET':
        packages = Package.objects.filter(is_active=True).order_by('name')
        package_data = []
        
        for item in packages:
            package_data.append({
                'id': str(item.id),
                'name': item.name,
                'description': item.description,
                'price': float(item.price),
                'features': item.features,
                'is_active': item.is_active,
                'created_at': item.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'data': package_data,
            'count': len(package_data)
        })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_package_detail(request, pk):
    """GET package detail"""
    if request.method == 'GET':
        try:
            package = get_object_or_404(Package, pk=pk, is_active=True)
            
            package_data = {
                'id': str(package.id),
                'name': package.name,
                'description': package.description,
                'price': float(package.price),
                'features': package.features,
                'is_active': package.is_active,
                'created_at': package.created_at.isoformat()
            }
            
            return JsonResponse({
                'success': True,
                'data': package_data
            })
        except Package.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Package not found'
            }, status=404)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_package_create(request):
    """POST to create package"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            serializer = PackageSerializer(data=data)
            if serializer.is_valid():
                package = serializer.save()
                return JsonResponse({
                    'success': True,
                    'data': PackageSerializer(package).data,
                    'message': 'Package created successfully'
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
def api_package_update(request, pk):
    """PUT to update package"""
    if request.method == 'PUT':
        try:
            package = get_object_or_404(Package, pk=pk)
            data = json.loads(request.body)
            serializer = PackageSerializer(package, data=data, partial=True)
            if serializer.is_valid():
                package = serializer.save()
                return JsonResponse({
                    'success': True,
                    'data': PackageSerializer(package).data,
                    'message': 'Package updated successfully'
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
def api_package_delete(request, pk):
    """DELETE to remove package"""
    if request.method == 'DELETE':
        try:
            package = get_object_or_404(Package, pk=pk)
            package.delete()
            return JsonResponse({
                'success': True,
                'message': 'Package deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)