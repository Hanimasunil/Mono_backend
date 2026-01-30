from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from django.shortcuts import redirect
from rest_framework.decorators import api_view
from rest_framework.response import Response
from .models import Blog
from .serializers import BlogSerializer, BlogListSerializer
import json

# Template Views
def blog_list(request):
    """Display list of published blogs"""
    blogs = Blog.objects.filter(status='published').order_by('-created_at')
    context = {
        'blogs': blogs,
        'page_title': 'Blog',
        'page_subtitle': 'Latest Articles'
    }
    return render(request, 'blogs/list.html', context)

def blog_detail(request, slug):
    """Display individual blog post"""
    blog = get_object_or_404(Blog, slug=slug, status='published')
    context = {
        'blog': blog,
        'page_title': blog.title,
        'page_subtitle': 'Blog Post'
    }
    return render(request, 'blogs/view.html', context)


def blog_preview(request, slug):
    """Preview individual blog post (includes drafts) - for admin use"""
    # Only allow if user is logged in as admin
    if not request.user.is_authenticated or not request.user.is_staff:
        from django.shortcuts import redirect
        return redirect('admin_login')
    
    blog = get_object_or_404(Blog, slug=slug)  # Don't restrict to published
    context = {
        'blog': blog,
        'page_title': blog.title,
        'page_subtitle': 'Blog Post Preview'
    }
    return render(request, 'blogs/view.html', context)


# Admin Views
@login_required(login_url='dashboard:admin_login')
def admin_blog_list(request):
    """Admin blog list view"""
    blogs = Blog.objects.all().order_by('-created_at')
    context = {
        'blogs': blogs,
        'page_title': 'Blog Management',
        'page_subtitle': 'Manage blog posts',
        'current_page': 'blog'
    }
    return render(request, 'admin/blog/list.html', context)

@login_required(login_url='dashboard:admin_login')
def admin_blog_add(request):
    """Admin add blog post"""
    if request.method == 'POST':
        title = request.POST.get('title')
        short_description = request.POST.get('short_description')
        content = request.POST.get('content')
        status = request.POST.get('status', 'draft')
        seo_title = request.POST.get('seo_title', '')
        seo_description = request.POST.get('seo_description', '')
        
        blog = Blog.objects.create(
            title=title,
            short_description=short_description,
            content=content,
            status=status,
            seo_title=seo_title,
            seo_description=seo_description
        )
        
        if status == 'published':
            blog.published_at = timezone.now()
            blog.save()
            
        return redirect('admin_blog_list')
    
    context = {
        'page_title': 'Add Blog Post',
        'page_subtitle': 'Create new blog post',
        'current_page': 'blog'
    }
    return render(request, 'admin/blog/add.html', context)

@login_required(login_url='dashboard:admin_login')
def admin_blog_edit(request, pk):
    """Admin edit blog post"""
    blog = get_object_or_404(Blog, pk=pk)
    
    if request.method == 'POST':
        blog.title = request.POST.get('title')
        blog.short_description = request.POST.get('short_description')
        blog.content = request.POST.get('content')
        blog.status = request.POST.get('status', 'draft')
        blog.seo_title = request.POST.get('seo_title', '')
        blog.seo_description = request.POST.get('seo_description', '')
        
        if blog.status == 'published' and not blog.published_at:
            blog.published_at = timezone.now()
        
        blog.save()
        
        return redirect('admin_blog_list')
    
    context = {
        'blog': blog,
        'page_title': f'Edit {blog.title}',
        'page_subtitle': 'Update blog post',
        'current_page': 'blog'
    }
    return render(request, 'admin/blog/edit.html', context)

@login_required(login_url='dashboard:admin_login')
def admin_blog_delete(request, pk):
    """Admin delete blog post"""
    blog = get_object_or_404(Blog, pk=pk)
    
    if request.method == 'POST':
        blog.delete()
        return redirect('admin_blog_list')
    
    context = {
        'blog': blog,
        'page_title': f'Delete {blog.title}',
        'page_subtitle': 'Confirm deletion',
        'current_page': 'blog'
    }
    return render(request, 'admin/blog/delete.html', context)

# API Views
@csrf_exempt
def api_blog_list(request):
    """GET blog list"""
    if request.method == 'GET':
        blogs = Blog.objects.filter(status='published').order_by('-created_at')
        blog_data = []
        
        for blog in blogs:
            blog_data.append({
                'id': str(blog.id),
                'title': blog.title,
                'slug': blog.slug,
                'short_description': blog.short_description,
                'cover_image': blog.cover_image.url if blog.cover_image else None,
                'seo_title': blog.seo_title,
                'status': blog.status,
                'published_at': blog.published_at.isoformat() if blog.published_at else None,
                'created_at': blog.created_at.isoformat()
            })
        
        return JsonResponse({
            'success': True,
            'data': blog_data,
            'count': len(blog_data)
        })
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)

@csrf_exempt
def api_blog_detail(request, slug):
    """GET blog detail (slug based)"""
    if request.method == 'GET':
        try:
            blog = get_object_or_404(Blog, slug=slug, status='published')
            
            blog_data = {
                'id': str(blog.id),
                'title': blog.title,
                'slug': blog.slug,
                'short_description': blog.short_description,
                'content': blog.content,
                'cover_image': blog.cover_image.url if blog.cover_image else None,
                'seo_title': blog.seo_title,
                'seo_description': blog.seo_description,
                'status': blog.status,
                'published_at': blog.published_at.isoformat() if blog.published_at else None,
                'created_at': blog.created_at.isoformat(),
                'updated_at': blog.updated_at.isoformat()
            }
            
            return JsonResponse({
                'success': True,
                'data': blog_data
            })
        except Blog.DoesNotExist:
            return JsonResponse({
                'success': False,
                'error': 'Blog not found'
            }, status=404)
    
    return JsonResponse({'success': False, 'error': 'Method not allowed'}, status=405)