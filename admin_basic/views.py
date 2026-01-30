import random
import datetime
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from .models import User, AdminOTP, Testimonial, Enquiry
from blog.models import Blog
from gallery.models import Gallery
from products.models import Product
from services.models import Service
from client.models import Client
from packages.models import Package
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.contrib.auth import login, logout
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse
from django.urls import reverse_lazy
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.contrib.auth.hashers import check_password
import json
from rest_framework.decorators import api_view
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
# DRF imports
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from rest_framework import status
from rest_framework import serializers
from django.contrib.auth import authenticate

# JWT imports
from rest_framework_simplejwt.tokens import RefreshToken


def admin_login(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        if not email:
            return render(request, 'login.html', {'error': 'Email is required'})
        
        # Validate email format
        if '@' not in email:
            return render(request, 'login.html', {'error': 'Please enter a valid email address'})
        
        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # Generate 6-digit OTP
        otp = str(random.randint(100000, 999999))
        
        # Set expiration time (10 minutes)
        expires_at = timezone.now() + datetime.timedelta(minutes=10)
        
        # Create OTP record
        AdminOTP.objects.create(
            user=user,
            otp=otp,
            otp_type='LOGIN',
            expires_at=expires_at
        )
        
        # Send OTP email
        try:
            send_mail(
                subject='Your Admin Login OTP',
                message=f'''Hello,

Your OTP for admin login is: {otp}

This OTP will expire in 10 minutes.

If you didn't request this OTP, please ignore this email.

Best regards,
Admin Team''',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            
            # Store user ID in session as string
            request.session['user_id'] = str(user.id)
            request.session['otp_sent'] = True
            
            return redirect('dashboard:verify_otp')
            
        except Exception as e:
            print(f"Email sending failed: {e}")
            return render(request, 'login.html', {
                'error': 'Failed to send OTP. Please check your email configuration.'
            })
    
    # Clear any existing session data
    request.session.flush()
    return render(request, 'login.html')


def verify_otp(request):
    # Check if user came from login page
    if 'user_id' not in request.session:
        return redirect('admin_login')
    
    user_id = request.session.get('user_id')
    
    if request.method == "POST":
        otp = request.POST.get("otp")
        
        if not otp:
            return render(request, 'otp.html', {'error': 'OTP is required'})
        
        if len(otp) != 6 or not otp.isdigit():
            return render(request, 'otp.html', {'error': 'Please enter a valid 6-digit OTP'})
        
        # Find valid OTP
        otp_obj = AdminOTP.objects.filter(
            user_id=user_id,
            otp=otp,
            otp_type='LOGIN',
            is_used=False
        ).first()
        
        # Check if OTP exists
        if not otp_obj:
            return render(request, 'otp.html', {'error': 'Invalid OTP'})
        
        # Check if OTP is expired
        if otp_obj.is_expired():
            return render(request, 'otp.html', {'error': 'OTP has expired. Please request a new one.'})
        
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()
        
        # Login user
        user = otp_obj.user
        login(request, user)
        
        # Clear session data
        request.session.pop('user_id', None)
        request.session.pop('otp_sent', None)
        
        # Redirect based on password status
        if not user.is_password_set:
            return redirect('dashboard:set_password')
        
        return redirect('dashboard:dashboard')
    
    # Check if OTP was sent
    if not request.session.get('otp_sent'):
        return redirect('admin_login')
    
    return render(request, 'otp.html')

def set_password(request):
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        if not password:
            return render(request, 'set_password.html', {'error': 'Password is required'})
        
        if len(password) < 8:
            return render(request, 'set_password.html', {'error': 'Password must be at least 8 characters long'})
        
        if password != confirm_password:
            return render(request, 'set_password.html', {'error': 'Passwords do not match'})
        
        user = request.user
        user.set_password(password)
        user.is_password_set = True
        user.save()
        
        # Re-authenticate user after password change
        login(request, user)
        
        return redirect('dashboard:dashboard')  # Redirect to dashboard after login
    
    # Prevent access if password is already set
    if request.user.is_authenticated and request.user.is_password_set:
        return redirect('dashboard:dashboard')
    
    return render(request, 'set_password.html')
def dashboard(request):
    if not request.user.is_authenticated:
        return redirect('dashboard:admin_login')
    
    context = {
        'page_title': 'Dashboard',
        'page_subtitle': 'Welcome to Admin Dashboard',
        'current_page': 'dashboard'
    }
    return render(request, 'dashboard.html', context)

def logout_view(request):
    logout(request)
    return redirect('dashboard:admin_login')

class TestimonialListView(LoginRequiredMixin, ListView):
    model = Testimonial
    template_name = 'testimonials/list.html'
    context_object_name = 'testimonials'
    login_url = 'dashboard:admin_login'
    ordering = ['-created_at']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Testimonials'
        context['page_subtitle'] = 'Manage customer testimonials'
        context['current_page'] = 'testimonials'
        print(f"Testimonials in context: {len(context['testimonials'])}")
        return context
    
    def get_queryset(self):
        queryset = super().get_queryset()
        print(f"Total testimonials in DB: {queryset.count()}")
        return queryset


class TestimonialCreateView(LoginRequiredMixin, CreateView):
    model = Testimonial
    template_name = 'testimonials/add.html'
    fields = ['name', 'designation', 'company', 'message', 'rating', 'is_active']
    success_url = reverse_lazy('dashboard:testimonials_list')
    login_url = 'dashboard:admin_login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Testimonial'
        context['page_subtitle'] = 'Create a new testimonial'
        context['current_page'] = 'testimonials'
        return context
    
    def form_valid(self, form):
        # Set default values if not provided
        if not form.instance.rating:
            form.instance.rating = 5
        response = super().form_valid(form)
        print(f"Testimonial saved: {form.instance.name}")  # Debug print
        return response
    
    def form_invalid(self, form):
        print(f"Form errors: {form.errors}")  # Debug print
        return super().form_invalid(form)


class TestimonialUpdateView(LoginRequiredMixin, UpdateView):
    model = Testimonial
    template_name = 'testimonials/add.html'
    fields = ['name', 'designation', 'company', 'message', 'rating', 'is_active']
    success_url = reverse_lazy('dashboard:testimonials_list')
    login_url = 'dashboard:admin_login'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Testimonial'
        context['page_subtitle'] = 'Update testimonial details'
        context['current_page'] = 'testimonials'
        return context


class TestimonialDetailView(LoginRequiredMixin, DetailView):
    model = Testimonial
    template_name = 'testimonials/view.html'
    login_url = 'dashboard:admin_login'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'View {self.object.name}'
        context['page_subtitle'] = 'Testimonial details'
        context['current_page'] = 'testimonials'
        return context


class TestimonialDeleteView(LoginRequiredMixin, DeleteView):
    model = Testimonial
    success_url = reverse_lazy('dashboard:testimonials_list')
    login_url = 'dashboard:admin_login'
    pk_url_kwarg = 'pk'
    
    def get(self, request, *args, **kwargs):
        # Allow GET requests for confirmation
        return self.post(request, *args, **kwargs)


class EnquiryListView(LoginRequiredMixin, ListView):
    model = Enquiry
    template_name = 'enquiries/list.html'
    context_object_name = 'enquiries'
    login_url = 'dashboard:admin_login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Enquiries'
        context['page_subtitle'] = 'Manage customer enquiries'
        context['current_page'] = 'enquiries'
        return context


class EnquiryCreateView(LoginRequiredMixin, CreateView):
    model = Enquiry
    template_name = 'enquiries/add.html'
    fields = ['name', 'email', 'phone', 'subject', 'message', 'source']
    success_url = reverse_lazy('dashboard:enquiries_list')
    login_url = 'dashboard:admin_login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Enquiry'
        context['page_subtitle'] = 'Create a new enquiry'
        context['current_page'] = 'enquiries'
        return context
    
    def form_valid(self, form):
        # Set default source if not provided
        if not form.instance.source:
            form.instance.source = 'web'
        response = super().form_valid(form)
        print(f"Enquiry saved: {form.instance.name}")  # Debug print
        return response
    
    def form_invalid(self, form):
        print(f"Form errors: {form.errors}")  # Debug print
        return super().form_invalid(form)


class EnquiryUpdateView(LoginRequiredMixin, UpdateView):
    model = Enquiry
    template_name = 'enquiries/add.html'
    fields = ['name', 'email', 'phone', 'subject', 'message', 'source', 'is_read']
    success_url = reverse_lazy('dashboard:enquiries_list')
    login_url = 'dashboard:admin_login'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Edit Enquiry'
        context['page_subtitle'] = 'Update enquiry details'
        context['current_page'] = 'enquiries'
        return context


class EnquiryDetailView(LoginRequiredMixin, DetailView):
    model = Enquiry
    template_name = 'enquiries/view.html'
    login_url = 'dashboard:admin_login'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'View Enquiry from {self.object.name}'
        context['page_subtitle'] = 'Enquiry details'
        context['current_page'] = 'enquiries'
        return context


class EnquiryDeleteView(LoginRequiredMixin, DeleteView):
    model = Enquiry
    success_url = reverse_lazy('dashboard:enquiries_list')
    login_url = 'dashboard:admin_login'
    pk_url_kwarg = 'pk'
    
    def get(self, request, *args, **kwargs):
        # Allow GET requests for confirmation
        return self.post(request, *args, **kwargs)

def forgot_password(request):
    if request.method == "POST":
        email = request.POST.get("email")
        
        if not email:
            return render(request, 'forgot_password.html', {'error': 'Email is required'})
        
        try:
            user = User.objects.get(email=email)
            
            # Generate 6-digit OTP
            otp = str(random.randint(100000, 999999))
            
            # Set expiration time (15 minutes)
            expires_at = timezone.now() + datetime.timedelta(minutes=15)
            
            # Create OTP record
            AdminOTP.objects.create(
                user=user,
                otp=otp,
                otp_type='PASSWORD_RESET',
                expires_at=expires_at
            )
            
            # Send OTP email
            send_mail(
                subject='Password Reset OTP',
                message=f'''Hello,

You have requested to reset your password.

Your OTP for password reset is: {otp}

This OTP will expire in 15 minutes.

If you didn't request this, please ignore this email.

Best regards,
Admin Team''',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            
            # Store user ID in session as string
            request.session['reset_user_id'] = str(user.id)
            request.session['reset_otp_sent'] = True
            
            return redirect('dashboard:reset_password_verify')
            
        except User.DoesNotExist:
            # Don't reveal if email exists for security
            pass
        
        return render(request, 'forgot_password.html', {
            'success': 'If the email exists in our system, you will receive an OTP shortly.'
        })
    
    return render(request, 'forgot_password.html')

def reset_password_verify(request):
    # Check if user came from forgot password page
    if 'reset_user_id' not in request.session:
        return redirect('dashboard:admin_login')
    
    if request.method == "POST":
        otp = request.POST.get("otp")
        
        if not otp:
            return render(request, 'reset_password_verify.html', {'error': 'OTP is required'})
        
        if len(otp) != 6 or not otp.isdigit():
            return render(request, 'reset_password_verify.html', {'error': 'Please enter a valid 6-digit OTP'})
        
        user_id = request.session.get('reset_user_id')
        
        # Find valid OTP
        otp_obj = AdminOTP.objects.filter(
            user_id=user_id,
            otp=otp,
            otp_type='PASSWORD_RESET',
            is_used=False
        ).first()
        
        # Check if OTP exists
        if not otp_obj:
            return render(request, 'reset_password_verify.html', {'error': 'Invalid OTP'})
        
        # Check if OTP is expired
        if otp_obj.is_expired():
            return render(request, 'reset_password_verify.html', {'error': 'OTP has expired. Please request a new one.'})
        
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()
        
        # Store user ID for password reset
        request.session['reset_verified_user_id'] = user_id
        
        return redirect('dashboard:reset_password')
    
    # Check if OTP was sent
    if not request.session.get('reset_otp_sent'):
        return redirect('dashboard:admin_login')
    
    return render(request, 'reset_password_verify.html')

def reset_password(request):
    # Check if user verified OTP
    if 'reset_verified_user_id' not in request.session:
        return redirect('dashboard:admin_login')
    
    user_id = request.session.get('reset_verified_user_id')
    
    if request.method == "POST":
        password = request.POST.get("password")
        confirm_password = request.POST.get("confirm_password")
        
        if not password:
            return render(request, 'reset_password.html', {'error': 'Password is required'})
        
        if len(password) < 8:
            return render(request, 'reset_password.html', {'error': 'Password must be at least 8 characters long'})
        
        if password != confirm_password:
            return render(request, 'reset_password.html', {'error': 'Passwords do not match'})
        
        try:
            user = User.objects.get(id=user_id)
            user.set_password(password)
            user.is_password_set = True
            user.save()
            
            # Clear all session data
            request.session.flush()
            
            return render(request, 'reset_password_success.html')
            
        except User.DoesNotExist:
            return redirect('dashboard:admin_login')
    
    return render(request, 'reset_password.html')


# ==================== SERIALIZERS ====================

class TestimonialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Testimonial
        fields = ['id', 'name', 'designation', 'company', 'message', 'rating', 'image', 'is_active', 'created_at']
        read_only_fields = ['id', 'created_at']


class TestimonialListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing testimonials"""
    short_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Testimonial
        fields = ['id', 'name', 'designation', 'company', 'short_message', 'rating', 'is_active', 'created_at']
    
    def get_short_message(self, obj):
        return obj.get_short_message()


class EnquirySerializer(serializers.ModelSerializer):
    class Meta:
        model = Enquiry
        fields = ['id', 'name', 'email', 'phone', 'subject', 'message', 'source', 'is_read', 'created_at']
        read_only_fields = ['id', 'created_at']


class EnquiryListSerializer(serializers.ModelSerializer):
    """Lightweight serializer for listing enquiries"""
    short_message = serializers.SerializerMethodField()
    
    class Meta:
        model = Enquiry
        fields = ['id', 'name', 'email', 'subject', 'short_message', 'source', 'is_read', 'created_at']
    
    def get_short_message(self, obj):
        return obj.get_short_message()


# ==================== API VIEWS ====================

@api_view(['POST'])
@permission_classes([AllowAny])
def api_admin_login(request):
    """API endpoint for admin login with OTP"""
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if not email:
            return Response({
                'success': False,
                'message': 'Email is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if '@' not in email:
            return Response({
                'success': False,
                'message': 'Please enter a valid email address'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Get or create user
        user, created = User.objects.get_or_create(
            email=email,
            defaults={
                'username': email.split('@')[0],
                'is_staff': True,
                'is_superuser': True
            }
        )
        
        # Generate OTP
        otp = str(random.randint(100000, 999999))
        expires_at = timezone.now() + datetime.timedelta(minutes=10)
        
        # Create OTP record
        AdminOTP.objects.create(
            user=user,
            otp=otp,
            otp_type='LOGIN',
            expires_at=expires_at
        )
        
        # Send OTP email
        try:
            send_mail(
                subject='Your Admin Login OTP',
                message=f'''Hello,

Your OTP for admin login is: {otp}

This OTP will expire in 10 minutes.

If you didn't request this OTP, please ignore this email.

Best regards,
Admin Team''',
                from_email=settings.EMAIL_HOST_USER,
                recipient_list=[email],
                fail_silently=False,
            )
            
            return Response({
                'success': True,
                'message': 'OTP sent successfully',
                'user_id': str(user.id)
            }, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({
                'success': False,
                'message': 'Failed to send OTP. Please check your email configuration.'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
            
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_verify_otp(request):
    """API endpoint to verify OTP"""
    try:
        data = json.loads(request.body)
        user_id = data.get('user_id')
        otp = data.get('otp')
        
        if not user_id or not otp:
            return Response({
                'success': False,
                'message': 'User ID and OTP are required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(otp) != 6 or not otp.isdigit():
            return Response({
                'success': False,
                'message': 'Please enter a valid 6-digit OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Find valid OTP
        otp_obj = AdminOTP.objects.filter(
            user_id=user_id,
            otp=otp,
            otp_type='LOGIN',
            is_used=False
        ).first()
        
        if not otp_obj:
            return Response({
                'success': False,
                'message': 'Invalid OTP'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if otp_obj.is_expired():
            return Response({
                'success': False,
                'message': 'OTP has expired. Please request a new one.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Mark OTP as used
        otp_obj.is_used = True
        otp_obj.save()
        
        user = otp_obj.user
        
        # Generate JWT tokens
        refresh = RefreshToken.for_user(user)
        
        response_data = {
            'success': True,
            'message': 'OTP verified successfully',
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': str(user.id),
                'email': user.email,
                'username': user.username,
                'is_password_set': user.is_password_set
            }
        }
        
        # Add redirect info based on password status
        if not user.is_password_set:
            response_data['redirect'] = 'set_password'
        else:
            response_data['redirect'] = 'dashboard'
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_set_password(request):
    """API endpoint to set password for first time"""
    try:
        data = json.loads(request.body)
        password = data.get('password')
        confirm_password = data.get('confirm_password')
        
        if not password:
            return Response({
                'success': False,
                'message': 'Password is required'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if len(password) < 8:
            return Response({
                'success': False,
                'message': 'Password must be at least 8 characters long'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        if password != confirm_password:
            return Response({
                'success': False,
                'message': 'Passwords do not match'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        user = request.user
        user.set_password(password)
        user.is_password_set = True
        user.save()
        
        return Response({
            'success': True,
            'message': 'Password set successfully',
            'redirect': 'dashboard'
        }, status=status.HTTP_200_OK)
        
    except json.JSONDecodeError:
        return Response({
            'success': False,
            'message': 'Invalid JSON data'
        }, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_logout(request):
    """API endpoint for logout"""
    try:
        # Blacklist the refresh token if provided
        try:
            refresh_token = request.data.get('refresh_token')
            if refresh_token:
                from rest_framework_simplejwt.tokens import RefreshToken
                token = RefreshToken(refresh_token)
                token.blacklist()
        except Exception:
            # If token is invalid or already blacklisted, continue
            pass
        
        return Response({
            'success': True,
            'message': 'Logged out successfully'
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_dashboard_stats(request):
    """API endpoint for dashboard statistics"""
    try:
        # Sample stats (you can replace with actual model counts)
        stats = {
            'total_users': User.objects.count(),
            'total_otps': AdminOTP.objects.count(),
            'active_users': User.objects.filter(is_active=True).count(),
            'unused_otps': AdminOTP.objects.filter(is_used=False, expires_at__gt=timezone.now()).count(),
            'testimonials': Testimonial.objects.count(),
            'active_testimonials': Testimonial.objects.filter(is_active=True).count(),
            'recent_testimonials': []
        }
        
        # Get recent testimonials
        recent_testimonials = Testimonial.objects.filter(is_active=True).order_by('-created_at')[:5]
        for testimonial in recent_testimonials:
            stats['recent_testimonials'].append({
                'id': str(testimonial.id),
                'name': testimonial.name,
                'designation': testimonial.designation,
                'company': testimonial.company,
                'rating': testimonial.rating,
                'message': testimonial.get_short_message(),
                'created_at': testimonial.created_at.isoformat(),
                'is_active': testimonial.is_active
            })
        
        # Add enquiry stats
        stats['enquiries'] = Enquiry.objects.count()
        stats['unread_enquiries'] = Enquiry.objects.filter(is_read=False).count()
        
        # Get recent enquiries
        recent_enquiries = Enquiry.objects.order_by('-created_at')[:5]
        stats['recent_enquiries'] = []
        for enquiry in recent_enquiries:
            stats['recent_enquiries'].append({
                'id': str(enquiry.id),
                'name': enquiry.name,
                'email': enquiry.email,
                'subject': enquiry.subject,
                'message': enquiry.get_short_message(),
                'source': enquiry.source,
                'is_read': enquiry.is_read,
                'created_at': enquiry.created_at.isoformat()
            })
        
        return Response({
            'success': True,
            'data': stats
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== TESTIMONIAL API VIEWS ====================

@api_view(['GET'])
@permission_classes([AllowAny])
def api_testimonial_list(request):
    """API endpoint to list active testimonials"""
    try:
        testimonials = Testimonial.objects.filter(is_active=True)
        serializer = TestimonialListSerializer(testimonials, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': testimonials.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_testimonial_create(request):
    """API endpoint to create a new testimonial (admin only)"""
    try:
        serializer = TestimonialSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Testimonial created successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_testimonial_detail(request, testimonial_id):
    """API endpoint to get testimonial details (admin only)"""
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        serializer = TestimonialSerializer(testimonial)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Testimonial.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Testimonial not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_testimonial_update(request, testimonial_id):
    """API endpoint to update testimonial (admin only)"""
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        serializer = TestimonialSerializer(testimonial, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Testimonial updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Testimonial.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Testimonial not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_testimonial_delete(request, testimonial_id):
    """API endpoint to delete testimonial (admin only)"""
    try:
        testimonial = Testimonial.objects.get(id=testimonial_id)
        testimonial.delete()
        
        return Response({
            'success': True,
            'message': 'Testimonial deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Testimonial.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Testimonial not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ==================== ENQUIRY API VIEWS ====================

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_enquiry_list(request):
    """API endpoint to list all enquiries"""
    try:
        # Filter by read/unread status if specified
        is_read_param = request.query_params.get('is_read', None)
        
        enquiries = Enquiry.objects.all()
        if is_read_param is not None:
            enquiries = enquiries.filter(is_read=(is_read_param.lower() == 'true'))
        
        # Order by creation date (newest first)
        enquiries = enquiries.order_by('-created_at')
        
        serializer = EnquiryListSerializer(enquiries, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data,
            'count': enquiries.count()
        }, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([AllowAny])
def api_enquiry_create(request):
    """API endpoint to create a new enquiry (public)"""
    try:
        serializer = EnquirySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Enquiry submitted successfully',
                'data': serializer.data
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_enquiry_detail(request, enquiry_id):
    """API endpoint to get enquiry details (admin only)"""
    try:
        enquiry = Enquiry.objects.get(id=enquiry_id)
        serializer = EnquirySerializer(enquiry)
        
        return Response({
            'success': True,
            'data': serializer.data
        }, status=status.HTTP_200_OK)
        
    except Enquiry.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Enquiry not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================= CLIENT API ENDPOINTS =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_client_list(request):
    """API endpoint to get all clients (admin only)"""
    from client.models import Client
    from client.serializers import ClientListSerializer
    
    clients = Client.objects.all()
    serializer = ClientListSerializer(clients, many=True)
    
    return Response({
        'success': True,
        'data': serializer.data,
        'count': len(serializer.data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_client_detail(request, pk):
    """API endpoint to get client details (admin only)"""
    from client.models import Client
    from client.serializers import ClientSerializer
    
    try:
        client = Client.objects.get(pk=pk)
        serializer = ClientSerializer(client)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
        
    except Client.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Client not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_client_create(request):
    """API endpoint to create a new client (admin only)"""
    from client.models import Client
    from client.serializers import ClientSerializer
    
    serializer = ClientSerializer(data=request.data)
    if serializer.is_valid():
        client = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Client created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'success': False,
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_client_update(request, pk):
    """API endpoint to update client (admin only)"""
    from client.models import Client
    from client.serializers import ClientSerializer
    
    try:
        client = Client.objects.get(pk=pk)
        serializer = ClientSerializer(client, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'success': True,
                'message': 'Client updated successfully',
                'data': serializer.data
            })
        else:
            return Response({
                'success': False,
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Client.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Client not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_client_delete(request, pk):
    """API endpoint to delete client (admin only)"""
    from client.models import Client
    
    try:
        client = Client.objects.get(pk=pk)
        client.delete()
        
        return Response({
            'success': True,
            'message': 'Client deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
        
    except Client.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Client not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_enquiry_update(request, enquiry_id):
    """API endpoint to update enquiry (admin only)"""
    try:
        enquiry = Enquiry.objects.get(id=enquiry_id)
        serializer = EnquirySerializer(enquiry, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({
                'success': True,
                'message': 'Enquiry updated successfully',
                'data': serializer.data
            }, status=status.HTTP_200_OK)
        else:
            return Response({
                'success': False,
                'message': 'Validation failed',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Enquiry.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Enquiry not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_enquiry_delete(request, enquiry_id):
    """API endpoint to delete enquiry (admin only)"""
    try:
        enquiry = Enquiry.objects.get(id=enquiry_id)
        enquiry.delete()
        
        return Response({
            'success': True,
            'message': 'Enquiry deleted successfully'
        }, status=status.HTTP_200_OK)
        
    except Enquiry.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Enquiry not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_enquiry_mark_read(request, enquiry_id):
    """API endpoint to mark enquiry as read (admin only)"""
    try:
        enquiry = Enquiry.objects.get(id=enquiry_id)
        enquiry.mark_as_read()
        
        return Response({
            'success': True,
            'message': 'Enquiry marked as read successfully',
            'data': EnquiryListSerializer(enquiry).data
        }, status=status.HTTP_200_OK)
        
    except Enquiry.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Enquiry not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

# ================= GALLERY API ENDPOINTS =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_gallery_list(request):
    """API endpoint to get all gallery items (admin only)"""
    from gallery.models import Gallery
    from gallery.serializers import GalleryListSerializer
    
    galleries = Gallery.objects.all()
    serializer = GalleryListSerializer(galleries, many=True)
    
    return Response({
        'success': True,
        'data': serializer.data,
        'count': len(serializer.data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_gallery_detail(request, pk):
    """API endpoint to get gallery item details (admin only)"""
    from gallery.models import Gallery
    from gallery.serializers import GallerySerializer
    
    try:
        gallery = Gallery.objects.get(pk=pk)
        serializer = GallerySerializer(gallery)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
        
    except Gallery.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Gallery item not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_gallery_create(request):
    """API endpoint to create a new gallery item (admin only)"""
    from gallery.models import Gallery
    from gallery.serializers import GallerySerializer
    
    serializer = GallerySerializer(data=request.data)
    if serializer.is_valid():
        gallery = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Gallery item created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'success': False,
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_gallery_update(request, pk):
    """API endpoint to update gallery item (admin only)"""
    from gallery.models import Gallery
    from gallery.serializers import GallerySerializer
    
    try:
        gallery = Gallery.objects.get(pk=pk)
        serializer = GallerySerializer(gallery, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'success': True,
                'message': 'Gallery item updated successfully',
                'data': serializer.data
            })
        else:
            return Response({
                'success': False,
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Gallery.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Gallery item not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_gallery_delete(request, pk):
    """API endpoint to delete gallery item (admin only)"""
    from gallery.models import Gallery
    
    try:
        gallery = Gallery.objects.get(pk=pk)
        gallery.delete()
        
        return Response({
            'success': True,
            'message': 'Gallery item deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
        
    except Gallery.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Gallery item not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Blog Views
@login_required(login_url='admin_login')
def blog_list_admin(request):
    """Admin blog list view"""
    blogs = Blog.objects.all().order_by('-created_at')
    context = {
        'blogs': blogs,
        'page_title': 'Blog Management',
        'page_subtitle': 'Manage blog posts',
        'current_page': 'blog'
    }
    return render(request, 'admin/blog/list.html', context)

@login_required(login_url='admin_login')
def blog_add(request):
    """Add new blog post"""
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
            
        return redirect('dashboard:blog_list_admin')
    
    context = {
        'page_title': 'Add Blog Post',
        'page_subtitle': 'Create new blog post',
        'current_page': 'blog'
    }
    return render(request, 'admin/blog/add.html', context)


# ================= PRODUCT VIEWS =================
@login_required
def product_list(request):
    from products.models import Product
    products = Product.objects.all()
    context = {
        'products': products,
        'page_title': 'Products',
        'page_subtitle': 'Manage your products',
        'current_page': 'products',
    }
    return render(request, 'products/list.html', context)

@login_required
def product_add(request):
    from products.models import Product
    from django.utils.text import slugify
    
    if request.method == 'POST':
        # Process the form data
        name = request.POST.get('name')
        description = request.POST.get('description')
        price = request.POST.get('price')
        is_active = request.POST.get('is_active') == 'on'
        
        # Handle image upload
        image = request.FILES.get('image')
        
        # Create slug from name
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
        
        # Debug print to check if messages is available
        print(f"messages object: {messages}")
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
    from products.models import Product
    from django.utils.text import slugify
    
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
def product_view(request, slug):
    from products.models import Product
    
    product = get_object_or_404(Product, slug=slug)
    
    context = {
        'product': product,
        'page_title': f'View {product.name}',
        'page_subtitle': 'Product details',
        'current_page': 'products',
    }
    return render(request, 'products/view.html', context)


@login_required
def product_delete(request, slug):
    from products.models import Product
    
    product = get_object_or_404(Product, slug=slug)
    
    if request.method == 'POST':
        product_name = product.name
        product.delete()
        messages.success(request, f'Product "{product_name}" has been deleted successfully.')
        return redirect('dashboard:product_list')
    
    context = {
        'product': product,
        'page_title': f'Delete {product.name}',
        'page_subtitle': 'Confirm deletion',
        'current_page': 'products',
    }
    return render(request, 'products/delete.html', context)


@login_required
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



@login_required
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
        return redirect('dashboard:gallery_list')
    
    context = {
        'page_title': 'Add Gallery Item',
        'page_subtitle': 'Upload a new gallery image',
        'current_page': 'gallery',
    }
    return render(request, 'gallery/add.html', context)


@login_required
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
        return redirect('dashboard:gallery_list')
    
    context = {
        'gallery_item': gallery_item,
        'page_title': f'Edit {gallery_item.title}',
        'page_subtitle': 'Update gallery image details',
        'current_page': 'gallery',
    }
    return render(request, 'gallery/add.html', context)


@login_required
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


@login_required
def gallery_delete(request, pk):
    """Delete a gallery image"""
    gallery_item = get_object_or_404(Gallery, pk=pk)
    
    if request.method == 'POST':
        item_title = gallery_item.title
        gallery_item.delete()
        messages.success(request, f'Gallery item "{item_title}" has been deleted successfully.')
        return redirect('dashboard:gallery_list')
    
    context = {
        'gallery_item': gallery_item,
        'page_title': f'Delete {gallery_item.title}',
        'page_subtitle': 'Confirm deletion',
        'current_page': 'gallery',
    }
    return render(request, 'gallery/delete.html', context)


@login_required
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



@login_required
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



@login_required
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



@login_required
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



@login_required
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


@login_required
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



@login_required
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



@login_required
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



@login_required
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



@login_required
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










@login_required
def service_view(request, pk):
    """View service details"""
    from services.models import Service
    service = get_object_or_404(Service, pk=pk)
    
    context = {
        'service': service,
        'page_title': f'View {service.name}',
        'page_subtitle': 'Service details',
        'current_page': 'services'
    }
    return render(request, 'services/view.html', context)



@login_required
def service_edit(request, pk):
    """Edit service"""
    from services.models import Service
    service = get_object_or_404(Service, pk=pk)
    
    if request.method == 'POST':
        service.name = request.POST.get('name')
        service.description = request.POST.get('description')
        service.is_active = request.POST.get('is_active') == 'on'
        service.save()
        
        return redirect('dashboard:service_list_admin')
    
    context = {
        'service': service,
        'page_title': f'Edit {service.name}',
        'page_subtitle': 'Update service details',
        'current_page': 'services'
    }
    return render(request, 'services/add.html', context)



@login_required
def service_delete(request, pk):
    """Delete service"""
    from services.models import Service
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


# ================= PRODUCT API ENDPOINTS =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_product_list(request):
    from products.models import Product
    from products.serializers import ProductListSerializer
    
    products = Product.objects.all()
    serializer = ProductListSerializer(products, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_product_create(request):
    from products.models import Product
    from products.serializers import ProductSerializer
    
    serializer = ProductSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_product_detail(request, slug):
    from products.models import Product
    from products.serializers import ProductDetailSerializer
    
    try:
        product = Product.objects.get(slug=slug)
        serializer = ProductDetailSerializer(product)
        return Response(serializer.data)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_product_update(request, slug):
    from products.models import Product
    from products.serializers import ProductSerializer
    
    try:
        product = Product.objects.get(slug=slug)
        serializer = ProductSerializer(product, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_product_delete(request, slug):
    from products.models import Product
    
    try:
        product = Product.objects.get(slug=slug)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Product.DoesNotExist:
        return Response({'error': 'Product not found'}, status=status.HTTP_404_NOT_FOUND)


# ================= SERVICE API ENDPOINTS =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_service_list(request):
    from services.models import Service
    from services.serializers import ServiceListSerializer
    
    services = Service.objects.all()
    serializer = ServiceListSerializer(services, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_service_create(request):
    from services.models import Service
    from services.serializers import ServiceSerializer
    
    serializer = ServiceSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_service_detail(request, slug):
    from services.models import Service
    from services.serializers import ServiceDetailSerializer
    
    try:
        service = Service.objects.get(slug=slug)
        serializer = ServiceDetailSerializer(service)
        return Response(serializer.data)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_service_update(request, slug):
    from services.models import Service
    from services.serializers import ServiceSerializer
    
    try:
        service = Service.objects.get(slug=slug)
        serializer = ServiceSerializer(service, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_service_delete(request, slug):
    from services.models import Service
    
    try:
        service = Service.objects.get(slug=slug)
        service.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
    except Service.DoesNotExist:
        return Response({'error': 'Service not found'}, status=status.HTTP_404_NOT_FOUND)


# ================= PACKAGES API ENDPOINTS =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_package_list(request):
    """API endpoint to get all packages (admin only)"""
    from packages.models import Package
    from packages.serializers import PackageListSerializer
    
    packages = Package.objects.all()
    serializer = PackageListSerializer(packages, many=True)
    
    return Response({
        'success': True,
        'data': serializer.data,
        'count': len(serializer.data)
    })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_package_detail(request, pk):
    """API endpoint to get package details (admin only)"""
    from packages.models import Package
    from packages.serializers import PackageSerializer
    
    try:
        package = Package.objects.get(pk=pk)
        serializer = PackageSerializer(package)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
        
    except Package.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Package not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_package_create(request):
    """API endpoint to create a new package (admin only)"""
    from packages.models import Package
    from packages.serializers import PackageSerializer
    
    # Parse features from JSON string if coming from form data
    data = request.data.copy()
    if 'features' in data and isinstance(data['features'], str):
        try:
            import json
            data['features'] = json.loads(data['features'])
        except json.JSONDecodeError:
            pass  # Keep as string if invalid JSON
    
    serializer = PackageSerializer(data=data)
    if serializer.is_valid():
        package = serializer.save()
        
        return Response({
            'success': True,
            'message': 'Package created successfully',
            'data': serializer.data
        }, status=status.HTTP_201_CREATED)
    else:
        return Response({
            'success': False,
            'message': 'Invalid data',
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT', 'PATCH'])
@permission_classes([IsAuthenticated])
def api_package_update(request, pk):
    """API endpoint to update package (admin only)"""
    from packages.models import Package
    from packages.serializers import PackageSerializer
    
    try:
        package = Package.objects.get(pk=pk)
        
        # Parse features from JSON string if coming from form data
        data = request.data.copy()
        if 'features' in data and isinstance(data['features'], str):
            try:
                import json
                data['features'] = json.loads(data['features'])
            except json.JSONDecodeError:
                pass  # Keep as string if invalid JSON
        
        serializer = PackageSerializer(package, data=data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            
            return Response({
                'success': True,
                'message': 'Package updated successfully',
                'data': serializer.data
            })
        else:
            return Response({
                'success': False,
                'message': 'Invalid data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
            
    except Package.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Package not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_package_delete(request, pk):
    """API endpoint to delete package (admin only)"""
    from packages.models import Package
    
    try:
        package = Package.objects.get(pk=pk)
        package.delete()
        
        return Response({
            'success': True,
            'message': 'Package deleted successfully'
        }, status=status.HTTP_204_NO_CONTENT)
        
    except Package.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Package not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# ================= BLOG API ENDPOINTS =================
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_blog_list_admin(request):
    from blog.models import Blog
    from blog.serializers import BlogListSerializer
    
    blogs = Blog.objects.all()
    serializer = BlogListSerializer(blogs, many=True)
    return Response(serializer.data)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_blog_create(request):
    from blog.models import Blog
    from blog.serializers import BlogSerializer
    
    serializer = BlogSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_blog_detail_admin(request, slug):
    from blog.models import Blog
    from blog.serializers import BlogDetailSerializer
    
    try:
        blog = Blog.objects.get(slug=slug)
        serializer = BlogDetailSerializer(blog)
        return Response(serializer.data)
    except Blog.DoesNotExist:
        return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def api_blog_update(request, slug):
    from blog.models import Blog
    from blog.serializers import BlogSerializer
    
    try:
        blog = Blog.objects.get(slug=slug)
        serializer = BlogSerializer(blog, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except Blog.DoesNotExist:
        return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)


@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def api_blog_delete(request, slug):
    from blog.models import Blog
    
    try:
        blog = Blog.objects.get(slug=slug)
        blog.delete()
        return Response(
    {"message": "Blog deleted successfully"},
    status=status.HTTP_200_OK
)

    except Blog.DoesNotExist:
        return Response({'error': 'Blog not found'}, status=status.HTTP_404_NOT_FOUND)
@login_required
@login_required(login_url='dashboard:admin_login')
def global_settings(request):
    """
    Global settings management view
    """
    from .models import GlobalSetting
    settings = GlobalSetting.objects.all()
    
    context = {
        'settings': settings,
        'user': request.user,
        'current_page': 'global_settings'
    }
    return render(request, 'global_settings.html', context)


# ================= GLOBAL SETTINGS VIEWS =================
@login_required(login_url='dashboard:admin_login')
def add_global_setting(request):
    """
    Add a new global setting
    """
    from .models import GlobalSetting
    if request.method == 'POST':
        key = request.POST.get('key')
        name = request.POST.get('name')
        value = request.POST.get('value', '')
        setting_type = request.POST.get('setting_type', 'TEXT')
        description = request.POST.get('description', '')
        is_active = request.POST.get('is_active') == 'on'
        
        try:
            setting = GlobalSetting.objects.create(
                key=key,
                name=name,
                value=value,
                setting_type=setting_type,
                description=description,
                is_active=is_active
            )
            messages.success(request, f'Setting "{name}" has been added successfully.')
        except Exception as e:
            messages.error(request, f'Error adding setting: {str(e)}')
        
        return redirect('dashboard:global_settings')
    
    return redirect('dashboard:global_settings')


@login_required(login_url='dashboard:admin_login')
def update_global_setting(request, pk):
    """
    Update an existing global setting
    """
    from .models import GlobalSetting
    setting = get_object_or_404(GlobalSetting, pk=pk)
    
    if request.method == 'POST':
        setting.name = request.POST.get('name')
        setting.value = request.POST.get('value', '')
        setting.is_active = request.POST.get('is_active') == 'on'
        
        try:
            setting.save()
            messages.success(request, f'Setting "{setting.name}" has been updated successfully.')
        except Exception as e:
            messages.error(request, f'Error updating setting: {str(e)}')
    
    return redirect('dashboard:global_settings')


@login_required(login_url='dashboard:admin_login')
def delete_global_setting(request, pk):
    """
    Delete a global setting
    """
    from .models import GlobalSetting
    setting = get_object_or_404(GlobalSetting, pk=pk)
    setting_name = setting.name
    
    try:
        setting.delete()
        messages.success(request, f'Setting "{setting_name}" has been deleted successfully.')
    except Exception as e:
        messages.error(request, f'Error deleting setting: {str(e)}')
    
    return redirect('dashboard:global_settings')


# ================= SERVICES VIEWS =================
class ServiceListView(LoginRequiredMixin, ListView):
    model = Service
    template_name = 'services/list.html'
    context_object_name = 'services'
    login_url = 'dashboard:admin_login'
    ordering = ['name']
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Service Management'
        context['page_subtitle'] = 'Manage services'
        context['current_page'] = 'services'

        return context


class ServiceCreateView(LoginRequiredMixin, CreateView):
    model = Service
    template_name = 'services/add.html'
    fields = ['name', 'description', 'is_active']
    success_url = reverse_lazy('dashboard:service_list_admin')
    login_url = 'dashboard:admin_login'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = 'Add Service'
        context['page_subtitle'] = 'Create new service'
        context['current_page'] = 'services'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Service "{form.instance.name}" has been added successfully.')
        return response


class ServiceUpdateView(LoginRequiredMixin, UpdateView):
    model = Service
    template_name = 'services/add.html'
    fields = ['name', 'description', 'is_active']
    success_url = reverse_lazy('dashboard:service_list_admin')
    login_url = 'dashboard:admin_login'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Edit {self.object.name}'
        context['page_subtitle'] = 'Update service details'
        context['current_page'] = 'services'
        return context
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f'Service "{form.instance.name}" has been updated successfully.')
        return response


class ServiceDetailView(LoginRequiredMixin, DetailView):
    model = Service
    template_name = 'services/view.html'
    login_url = 'dashboard:admin_login'
    pk_url_kwarg = 'pk'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'View {self.object.name}'
        context['page_subtitle'] = 'Service details'
        context['current_page'] = 'services'
        return context


class ServiceDeleteView(LoginRequiredMixin, DeleteView):
    model = Service
    success_url = reverse_lazy('dashboard:service_list_admin')
    login_url = 'dashboard:admin_login'
    pk_url_kwarg = 'pk'
    template_name = 'services/delete.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['page_title'] = f'Delete {self.object.name}'
        context['page_subtitle'] = 'Confirm deletion'
        context['current_page'] = 'services'
        return context
    
    def delete(self, request, *args, **kwargs):
        service = self.get_object()
        service_name = service.name
        response = super().delete(request, *args, **kwargs)
        messages.success(request, f'Service "{service_name}" has been deleted successfully.')
        return response