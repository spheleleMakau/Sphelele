from datetime import datetime, time
import json

from django.http import JsonResponse
from django.views.decorators.http import require_http_methods

from .models import Appointment, BlockedTime, Client, Service


def services(request):
    data = list(Service.objects.filter(active=True).values('id', 'name', 'description', 'duration_minutes', 'price', 'deposit_amount'))
    return JsonResponse({'services': data})


def availability(request):
    date_value = request.GET.get('date')
    service_id = request.GET.get('service')
    if not date_value or not service_id:
        return JsonResponse({'error': 'date and service are required'}, status=400)
    service = Service.objects.get(id=service_id, active=True)
    booked = set(Appointment.objects.filter(date=date_value, status__in=['PENDING', 'CONFIRMED']).values_list('start_time', flat=True))
    blocked = list(BlockedTime.objects.filter(date=date_value).values('start_time', 'end_time', 'reason'))
    slots = []
    current = 8 * 60
    closing = 19 * 60
    while current + service.duration_minutes <= closing:
        start = time(current // 60, current % 60)
        slots.append({'time': start.strftime('%H:%M'), 'available': start not in booked, 'reason': 'Booked' if start in booked else ''})
        current += 60
    return JsonResponse({'date': date_value, 'timezone': 'Africa/Johannesburg', 'duration_minutes': service.duration_minutes, 'slots': slots, 'blocked': blocked})


@require_http_methods(['GET', 'POST'])
def appointments(request):
    if request.method == 'GET':
        appointments = Appointment.objects.filter(deposit_paid=True).select_related('client', 'service')
        data = [{'id': item.id, 'client': item.client.name, 'whatsapp': item.client.whatsapp, 'service': item.service.name, 'date': item.date, 'start_time': item.start_time, 'status': item.status} for item in appointments]
        return JsonResponse({'appointments': data})
    try:
        payload = json.loads(request.body)
        service = Service.objects.get(id=payload['service'], active=True)
        date_value = payload['date']
        start_value = datetime.strptime(payload['start_time'], '%H:%M').time()
    except (KeyError, ValueError, Service.DoesNotExist, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid booking details'}, status=400)
    if Appointment.objects.filter(date=date_value, start_time=start_value, status__in=['PENDING', 'CONFIRMED']).exists():
        return JsonResponse({'error': 'This time is no longer available'}, status=409)
    client = Client.objects.create(name=payload['name'], whatsapp=payload['whatsapp'], note=payload.get('note', ''))
    return JsonResponse({'status': 'payment_required', 'deposit_amount': service.deposit_amount, 'client_id': client.id}, status=202)
