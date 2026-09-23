import json

from django.test import TestCase

from booking.models import Appointment, Service


class AppointmentAPITest(TestCase):
    def setUp(self):
        self.service = Service.objects.create(
            name='Classic Lashes',
            description='Soft, timeless definition.',
            duration_minutes=90,
            price=300,
            deposit_amount=100,
            active=True,
        )

    def test_booking_creation_persists_and_appears_in_admin_list(self):
        payload = {
            'service_id': self.service.id,
            'date': '2026-09-25',
            'start_time': '09:00',
            'name': 'Alicia Smith',
            'whatsapp': '0712345678',
            'note': 'Please keep it gentle.',
            'deposit_paid': True,
            'status': 'CONFIRMED',
        }

        response = self.client.post(
            '/api/appointments/',
            data=json.dumps(payload),
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 201)
        self.assertEqual(Appointment.objects.count(), 1)
        appointment = Appointment.objects.get()
        self.assertTrue(appointment.deposit_paid)
        self.assertEqual(appointment.status, Appointment.Status.CONFIRMED)

        list_response = self.client.get('/api/appointments/')
        self.assertEqual(list_response.status_code, 200)
        data = json.loads(list_response.content)
        self.assertEqual(len(data['appointments']), 1)
        self.assertEqual(data['appointments'][0]['client'], 'Alicia Smith')
