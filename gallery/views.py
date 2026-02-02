from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Gallery
from .serializers import GallerySerializer
import json

@login_required(login_url='dashboard:admin_login')
def gallery_list(request):
    """List all gallery images"""
    gallery_items = Gallery.objects.all().order_by('-created_at')
    context = {
        'gallery_items': gallery_items,
        'page_title': 'Gallery',
        'page_subtitle': 'Manage gallery images',
        'current_page': 'gallery',
    }
    return render(request, 'gallery/list.html', context)


@login_required(login_url='dashboard:admin_login')
def gallery_add(request):
    """Add a new gallery image"""
    if request.method == 'POST':
        title = request.POST.get('title')
        category = request.POST.get('category')
        is_active = request.POST.get('is_active') == 'on'
        
        # Handle image upload
        image = request.FILES.get('image')
        
        gallery_item = Gallery.objects.create(
            title=title,
            category=category,
            image=image,
            is_active=is_active
        )
        
        messages.success(request, f'Gallery item "{title}" has been added successfully.')
        return redirect('gallery_list')
    
    context = {
        'page_title': 'Add Gallery Item',
        'page_subtitle': 'Upload a new gallery image',
        'current_page': 'gallery',
    }
    return render(request, 'gallery/add.html', context)


@login_required(login_url='dashboard:admin_login')
def gallery_edit(request, pk):
    """Edit a gallery image"""
    gallery_item = get_object_or_404(Gallery, pk=pk)
    
    if request.method == 'POST':
        gallery_item.title = request.POST.get('title')
        gallery_item.category = request.POST.get('category')
        gallery_item.is_active = request.POST.get('is_active') == 'on'
        
        # Handle image upload
        if 'image' in request.FILES:
            gallery_item.image = request.FILES.get('image')
        
        gallery_item.save()
        
        messages.success(request, f'Gallery item "{gallery_item.title}" has been updated successfully.')
        return redirect('gallery_list')
    
    context = {
        'gallery_item': gallery_item,
        'page_title': f'Edit {gallery_item.title}',
        'page_subtitle': 'Update gallery image details',
        'current_page': 'gallery',
    }
    return render(request, 'gallery/add.html', context)


@login_required(login_url='dashboard:admin_login')
def gallery_view(request, pk):
    """View gallery image details"""
    gallery_item = get_object_or_404(Gallery, pk=pk)
    
    context = {
        'gallery_item': gallery_item,
        'page_title': f'View {gallery_item.title}',
        'page_subtitle': 'Gallery image details',
        'current_page': 'gallery',
    }
    return render(request, 'gallery/view.html', context)


@login_required(login_url='dashboard:admin_login')
def gallery_delete(request, pk):
    """Delete a gallery image"""
    gallery_item = get_object_or_404(Gallery, pk=pk)
    
    if request.method == 'POST':
        item_title = gallery_item.title
        gallery_item.delete()
        messages.success(request, f'Gallery item "{item_title}" has been deleted successfully.')
        return redirect('gallery_list')
    
    context = {
        'gallery_item': gallery_item,
        'page_title': f'Delete {gallery_item.title}',
        'page_subtitle': 'Confirm deletion',
        'current_page': 'gallery',
    }
    return render(request, 'gallery/delete.html', context)


# API Views
@csrf_exempt
def api_gallery_list(request):
    """GET gallery list"""
    if request.method == 'GET':
        gallery_items = Gallery.objects.filter(is_active=True).order_by('-created_at')
        gallery_data = []
        
        for item in gallery_items:
            gallery_data.append({
                'id': str(item.id),
                'title': item.title,
                'image': item.image.url if item.image else None,
                'category': item.category,
                'is_active': item.is_active,
                'created_at': item.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'data': gallery_data,
            'count': len(gallery_data)
        })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_gallery_detail(request, pk):
    """GET gallery detail"""
    if request.method == 'GET':
        try:
            gallery_item = get_object_or_404(Gallery, pk=pk, is_active=True)
            
            gallery_data = {
                'id': str(gallery_item.id),
                'title': gallery_item.title,
                'image': gallery_item.image.url if gallery_item.image else None,
                'category': gallery_item.category,
                'is_active': gallery_item.is_active,
                'created_at': gallery_item.created_at.isoformat()
            }
            
            return JsonResponse({
                'success': True,
                'data': gallery_data
            })
        except Gallery.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Gallery item not found'
            }, status=404)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_gallery_create(request):
    """POST to create gallery item"""
    if request.method == 'POST':
        try:
            # Handle both JSON and multipart form data
            if request.content_type.startswith('application/json'):
                data = json.loads(request.body)
                # Create a gallery item without saving to handle file uploads separately
                gallery_item = Gallery(
                    title=data.get('title', ''),
                    category=data.get('category', ''),
                    is_active=data.get('is_active', True)
                )
                # Note: Image upload not supported with JSON data
                gallery_item.save()
                
                return JsonResponse({
                    'success': True,
                    'data': GallerySerializer(gallery_item).data,
                    'message': 'Gallery item created successfully'
                })
            else:
                # Handle multipart form data (file uploads)
                title = request.POST.get('title')
                category = request.POST.get('category', '')
                is_active = request.POST.get('is_active', 'true').lower() == 'true'
                image = request.FILES.get('image')
                
                gallery_item = Gallery.objects.create(
                    title=title,
                    category=category,
                    is_active=is_active,
                    image=image
                )
                
                return JsonResponse({
                    'success': True,
                    'data': GallerySerializer(gallery_item).data,
                    'message': 'Gallery item created successfully'
                })
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_gallery_update(request, pk):
    """PUT to update gallery item"""
    if request.method == 'PUT':
        try:
            gallery_item = get_object_or_404(Gallery, pk=pk)
            
            # Handle both JSON and multipart form data
            if request.content_type.startswith('application/json'):
                data = json.loads(request.body)
                serializer = GallerySerializer(gallery_item, data=data, partial=True)
                if serializer.is_valid():
                    gallery_item = serializer.save()
                    return JsonResponse({
                        'success': True,
                        'data': GallerySerializer(gallery_item).data,
                        'message': 'Gallery item updated successfully'
                    })
                else:
                    return JsonResponse({
                        'success': False,
                        'error': serializer.errors
                    }, status=400)
            else:
                # Handle multipart form data (file uploads)
                title = request.POST.get('title', gallery_item.title)
                category = request.POST.get('category', gallery_item.category)
                is_active = request.POST.get('is_active', '').lower() == 'true' if request.POST.get('is_active') else gallery_item.is_active
                
                # Handle image upload if provided
                if 'image' in request.FILES:
                    gallery_item.image = request.FILES.get('image')
                
                gallery_item.title = title
                gallery_item.category = category
                gallery_item.is_active = is_active
                gallery_item.save()
                
                return JsonResponse({
                    'success': True,
                    'data': GallerySerializer(gallery_item).data,
                    'message': 'Gallery item updated successfully'
                })
        except json.JSONDecodeError:
            return JsonResponse({
                'success': False,
                'error': 'Invalid JSON data'
            }, status=400)
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_gallery_delete(request, pk):
    """DELETE to remove gallery item"""
    if request.method == 'DELETE':
        try:
            gallery_item = get_object_or_404(Gallery, pk=pk)
            gallery_item.delete()
            return JsonResponse({
                'success': True,
                'message': 'Gallery item deleted successfully'
            })
        except Exception as e:
            return JsonResponse({
                'success': False,
                'error': str(e)
            }, status=400)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)
