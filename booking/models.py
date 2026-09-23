from datetime import datetime, timedelta

from django.db import models


class Service(models.Model):
    name = models.CharField(max_length=120)
    description = models.TextField(blank=True)
    duration_minutes = models.PositiveIntegerField()
    price = models.DecimalField(max_digits=8, decimal_places=2)
    deposit_amount = models.DecimalField(max_digits=8, decimal_places=2)
    active = models.BooleanField(default=True)

    def __str__(self):
        return self.name


class Client(models.Model):
    name = models.CharField(max_length=120)
    whatsapp = models.CharField(max_length=30)
    note = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class Appointment(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pending payment'
        CONFIRMED = 'CONFIRMED', 'Confirmed'
        COMPLETED = 'COMPLETED', 'Completed'
        CANCELLED = 'CANCELLED', 'Cancelled'

    client = models.ForeignKey(Client, on_delete=models.PROTECT, related_name='appointments')
    service = models.ForeignKey(Service, on_delete=models.PROTECT)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    deposit_paid = models.BooleanField(default=False)
    payment_reference = models.CharField(max_length=120, blank=True)
    timezone = models.CharField(max_length=60, default='Africa/Johannesburg')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['date', 'start_time'], name='unique_appointment_start'),
        ]
        ordering = ['date', 'start_time']

    def __str__(self):
        return f'{self.service} - {self.date} {self.start_time}'

    @property
    def started(self):
        now = datetime.combine(self.date, datetime.now().time())
        start_dt = datetime.combine(self.date, self.start_time)
        return now >= start_dt

    @property
    def expired(self):
        end_dt = datetime.combine(self.date, self.end_time)
        if end_dt < datetime.now():
            return True
        return False


class BlockedTime(models.Model):
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    reason = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ['date', 'start_time']
