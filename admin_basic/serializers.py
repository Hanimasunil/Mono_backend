from rest_framework import serializers
from .models import User, AdminOTP, Testimonial, Enquiry


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_password_set', 'created_at']
        read_only_fields = ['id', 'created_at', 'is_password_set']


class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'


class TestimonialListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'name', 'company', 'rating', 'is_active', 'created_at']


class TestimonialDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = '__all__'


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = '__all__'


class EnquiryListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = ['id', 'name', 'email', 'subject', 'is_read', 'created_at']


class EnquiryDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = '__all__'