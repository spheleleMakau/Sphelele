from django.db import migrations


def remove_hd_lace_bookings(apps, schema_editor):
    Appointment = apps.get_model('booking', 'Appointment')
    Service = apps.get_model('booking', 'Service')
    hd_lace = Service.objects.filter(name='HD Lace Installation').first()
    if hd_lace:
        Appointment.objects.filter(service=hd_lace).delete()
        hd_lace.delete()


class Migration(migrations.Migration):
    dependencies = [('booking', '0002_seed_services')]
    operations = [migrations.RunPython(remove_hd_lace_bookings, migrations.RunPython.noop)]
