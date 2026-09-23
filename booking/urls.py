from django.urls import path
from . import views

urlpatterns = [
    path('services/', views.services, name='services'),
    path('availability/', views.availability, name='availability'),
    path('appointments/', views.appointments, name='appointments'),
    path('appointments/<int:appointment_id>/dummy-payment/', views.dummy_payment, name='dummy_payment'),
]
