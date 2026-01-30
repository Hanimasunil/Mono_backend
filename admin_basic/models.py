from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
import uuid

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    is_password_set = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']


class AdminOTP(models.Model):
    OTP_TYPES = [
        ('LOGIN', 'Login OTP'),
        ('PASSWORD_RESET', 'Password Reset OTP'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp = models.CharField(max_length=6)
    otp_type = models.CharField(max_length=20, choices=OTP_TYPES, default='LOGIN')
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.user.email} - {self.otp} ({self.otp_type})"
    
    def is_expired(self):
        return timezone.now() > self.expires_at


class Testimonial(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=150)
    designation = models.CharField(max_length=150, blank=True)
    company = models.CharField(max_length=150, blank=True)
    message = models.TextField()
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)], default=5)
    image = models.ImageField(upload_to='testimonials/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Testimonial'
        verbose_name_plural = 'Testimonials'
    
    def __str__(self):
        return f"{self.name} - {self.company}"
    
    def get_short_message(self):
        """Return truncated message for display"""
        return self.message[:100] + '...' if len(self.message) > 100 else self.message

class Enquiry(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=100)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True)
    subject = models.CharField(max_length=200)
    message = models.TextField()
    SOURCE_CHOICES = [
        ('web', 'Web'),
        ('service', 'Service'),
        ('product', 'Product'),
    ]
    source = models.CharField(max_length=20, choices=SOURCE_CHOICES, default='web')
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Enquiry'
        verbose_name_plural = 'Enquiries'
    
    def __str__(self):
        return f"{self.subject} - {self.name} ({self.email})"
    
    def mark_as_read(self):
        """Mark the enquiry as read"""
        self.is_read = True
        self.save(update_fields=['is_read'])
    
    def get_short_message(self):
        """Return truncated message for display"""
        return self.message[:100] + '...' if len(self.message) > 100 else self.message


class GlobalSetting(models.Model):
    SETTING_TYPES = [
        ('TEXT', 'Text'),
        ('TEXTAREA', 'Text Area'),
        ('BOOLEAN', 'Boolean'),
        ('IMAGE', 'Image'),
        ('EMAIL', 'Email'),
        ('URL', 'URL'),
    ]
    
    key = models.CharField(max_length=100, unique=True, help_text="Unique setting identifier")
    name = models.CharField(max_length=200, help_text="Display name for the setting")
    value = models.TextField(help_text="Setting value")
    setting_type = models.CharField(max_length=20, choices=SETTING_TYPES, default='TEXT')
    description = models.TextField(blank=True, help_text="Description of the setting")
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Global Setting'
        verbose_name_plural = 'Global Settings'
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name} ({self.key})"
