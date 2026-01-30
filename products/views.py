from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Product

@login_required
def product_list(request):
    products = Product.objects.all()
    context = {
        'products': products,
        'page_title': 'Products',
        'page_subtitle': 'Manage your products',
        'current_page': 'products',
    }
    return render(request, 'products/list.html', context)

@login_required
def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug)
    context = {
        'product': product,
        'page_title': product.name,
        'current_page': 'products',
    }
    return render(request, 'products/view.html', context)

@login_required
def product_add(request):
    if request.method == 'POST':
        # Process the form data
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        is_active = request.POST.get('is_active') == 'on'
        
        # Handle image upload
        image = request.FILES.get('image')
        
        # Create slug from name
        from django.utils.text import slugify
        slug = slugify(name)
        
        # Create the product
        product = Product(
            name=name,
            slug=slug,
            description=description,
            price=price,
            image=image,
            is_active=is_active,
        )
        product.save()
        
        messages.success(request, f'Product "{name}" has been created successfully.')
        return redirect('dashboard:product_list')
    
    context = {
        'page_title': 'Add Product',
        'page_subtitle': 'Create a new product',
        'current_page': 'products',
    }
    return render(request, 'products/add.html', context)

@login_required
def product_edit(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        # Process the form data
        product.name = request.POST.get('name')
        product.description = request.POST.get('description')
        product.price = request.POST.get('price')
        product.is_active = request.POST.get('is_active') == 'on'
        
        # Handle image upload
        if 'image' in request.FILES:
            product.image = request.FILES.get('image')
        
        # Update slug from name if name changed
        if product.name != request.POST.get('name_original'):
            from django.utils.text import slugify
            product.slug = slugify(product.name)
        
        product.save()
        
        messages.success(request, f'Product "{product.name}" has been updated successfully.')
        return redirect('dashboard:product_list')
    
    context = {
        'product': product,
        'page_title': f'Edit {product.name}',
        'page_subtitle': 'Update product details',
        'current_page': 'products',
    }
    return render(request, 'products/edit.html', context)

@login_required
def product_delete(request, slug):
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" has been deleted successfully.')
        return redirect('dashboard:product_list')
    
    context = {
        'product': product,
        'page_title': f'Delete {product.name}',
        'current_page': 'products',
    }
    return render(request, 'products/delete.html', context)


# API Views
@csrf_exempt
def api_product_list(request):
    """GET product list"""
    if request.method == 'GET':
        products = Product.objects.filter(is_active=True).order_by('-created_at')
        product_data = []
        
        for product in products:
            product_data.append({
                'id': str(product.id),
                'name': product.name,
                'slug': product.slug,
                'description': product.description,
                'price': float(product.price),
                'image': product.image.url if product.image else None,
                'is_active': product.is_active,
                'created_at': product.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'data': product_data,
            'count': len(product_data)
        })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)


@csrf_exempt
def api_product_detail(request, slug):
    """GET product detail (slug based)"""
    if request.method == 'GET':
        try:
            product = get_object_or_404(Product, slug=slug, is_active=True)
            
            product_data = {
                'id': str(product.id),
                'name': product.name,
                'slug': product.slug,
                'description': product.description,
                'price': float(product.price),
                'image': product.image.url if product.image else None,
                'is_active': product.is_active,
                'created_at': product.created_at.isoformat()
            }
            
            return JsonResponse({
                'success': True,
                'data': product_data
            })
        except Product.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Product not found'
            }, status=404)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

