from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect


def home(request):
    return JsonResponse({
        'service': 'Sphelele API',
        'status': 'ok',
        'frontend_url': settings.FRONTEND_URL or None,
        'endpoints': ['/api/services/', '/api/availability/', '/api/appointments/', '/admin/'],
        'message': 'This is the API service. The public booking page should be served from the static frontend host.'
    })

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('booking.urls')),
]
