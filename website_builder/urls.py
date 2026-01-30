from django.contrib import admin
from django.urls import path, include
from django.shortcuts import redirect
from django.conf import settings
from django.conf.urls.static import static
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path('', lambda request: redirect('dashboard:admin_login')),  # Redirect home to login
    path('django-admin/', admin.site.urls),
    path('admin/', include('admin_basic.urls', namespace='dashboard')),
    path('blog/', include('blog.urls')),
    path('products/', include('products.urls')),
    path('services/', include('services.urls')),
    path('gallery/', include('gallery.urls')),
    path('clients/', include('client.urls')),
    path('packages/', include('packages.urls')),
    path('bookingslots/', include('bookingslots.urls')),
    
    # JWT token endpoints
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
] 
if settings.DEBUG:
    urlpatterns += static(
        settings.MEDIA_URL,
        document_root=settings.MEDIA_ROOT
    )