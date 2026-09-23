from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.http import JsonResponse
from django.shortcuts import redirect


def home(request):
    if settings.FRONTEND_URL:
        return redirect(settings.FRONTEND_URL)
    return JsonResponse({'service': 'Sphelele API', 'status': 'ok', 'endpoints': ['/api/services/', '/api/availability/', '/api/appointments/', '/admin/']})

urlpatterns = [
    path('', home, name='home'),
    path('admin/', admin.site.urls),
    path('api/', include('booking.urls')),
]
