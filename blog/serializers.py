from rest_framework import serializers
from .models import Blog

class BlogSerializer(serializers.ModelSerializer):
    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'short_description', 'content',
            'cover_image', 'seo_title', 'seo_description', 'status',
            'published_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']

class BlogListSerializer(serializers.ModelSerializer):
    """Simplified serializer for blog list endpoint"""
    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'short_description',
            'cover_image', 'seo_title', 'status',
            'published_at', 'created_at'
        ]
        read_only_fields = ['id', 'created_at']


class BlogDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for blog detail endpoint"""
    class Meta:
        model = Blog
        fields = [
            'id', 'title', 'slug', 'short_description', 'content',
            'cover_image', 'seo_title', 'seo_description', 'status',
            'published_at', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']