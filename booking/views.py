from datetime import datetime, timedelta, time
import json

from django.db import transaction
from django.http import JsonResponse
from django.utils import timezone
from django.views.decorators.http import require_http_methods

from .models import Appointment, BlockedTime, Client, Service


def cleanup_expired_appointments():
    cutoff = timezone.now() - timedelta(hours=2)
    expired = Appointment.objects.filter(
        deposit_paid=True,
        status__in=[Appointment.Status.CONFIRMED, Appointment.Status.PENDING],
        created_at__lt=cutoff,
    )
    expired.delete()


def services(request):
    cleanup_expired_appointments()
    data = list(Service.objects.filter(active=True).values('id', 'name', 'description', 'duration_minutes', 'price', 'deposit_amount'))
    return JsonResponse({'services': data})


def availability(request):
    cleanup_expired_appointments()
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
    cleanup_expired_appointments()
    if request.method == 'GET':
        appointments = Appointment.objects.filter(deposit_paid=True).select_related('client', 'service')
        data = [{
            'id': item.id,
            'client': item.client.name,
            'whatsapp': item.client.whatsapp,
            'service': item.service.name,
            'date': item.date.isoformat(),
            'start_time': item.start_time.strftime('%H:%M'),
            'status': item.status,
            'deposit_paid': item.deposit_paid,
        } for item in appointments]
        return JsonResponse({'appointments': data})

    try:
        payload = json.loads(request.body)
        service_id = payload.get('service_id') or payload.get('service')
        service = Service.objects.get(id=service_id, active=True)
        date_value = payload['date']
        start_value = datetime.strptime(payload['start_time'], '%H:%M').time()
        end_value = datetime.strptime(payload['end_time'] if 'end_time' in payload else (datetime.strptime(payload['start_time'], '%H:%M') + __import__('datetime').timedelta(minutes=service.duration_minutes)).strftime('%H:%M'), '%H:%M').time()
    except (KeyError, ValueError, TypeError, Service.DoesNotExist, json.JSONDecodeError):
        return JsonResponse({'error': 'Invalid booking details'}, status=400)

    if Appointment.objects.filter(date=date_value, start_time=start_value, status__in=['PENDING', 'CONFIRMED']).exists():
        return JsonResponse({'error': 'This time is no longer available'}, status=409)

    with transaction.atomic():
        client = Client.objects.create(
            name=payload['name'],
            whatsapp=payload['whatsapp'],
            note=payload.get('note', ''),
        )
        appointment = Appointment.objects.create(
            client=client,
            service=service,
            date=date_value,
            start_time=start_value,
            end_time=end_value,
            status=payload.get('status', Appointment.Status.PENDING),
            deposit_paid=bool(payload.get('deposit_paid', False)),
            timezone=payload.get('timezone', 'Africa/Johannesburg'),
        )

    if bool(payload.get('deposit_paid', False)):
        return JsonResponse({
            'status': 'confirmed',
            'message': 'Appointment saved and visible in admin.',
            'appointment_id': appointment.id,
            'client_id': client.id,
            'deposit_amount': service.deposit_amount,
        }, status=201)

    return JsonResponse({
        'status': 'payment_required',
        'deposit_amount': service.deposit_amount,
        'client_id': client.id,
    }, status=202)
