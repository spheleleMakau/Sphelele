from pathlib import Path

from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.http import FileResponse, JsonResponse

BASE_DIR = Path(__file__).resolve().parent.parent


def home(request):
    accepts_html = 'text/html' in request.headers.get('Accept', '')
    if accepts_html:
        html_path = BASE_DIR / 'index.html'
        if html_path.exists():
            return FileResponse(html_path.open('rb'), content_type='text/html; charset=utf-8')

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
