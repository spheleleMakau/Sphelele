from django.db import migrations


SERVICES = [
    ('HD Lace Installation', 'Natural-looking melt and customised styling.', 150, 500, 150),
    ('Frontal Installation', 'Secure, seamless and styled for your everyday.', 120, 450, 150),
    ('Classic Lashes', 'Soft, timeless definition.', 90, 300, 100),
    ('Hybrid Lashes', 'The balance of volume and natural texture.', 105, 350, 100),
]


def create_services(apps, schema_editor):
    Service = apps.get_model('booking', 'Service')
    Service.objects.bulk_create([
        Service(name=name, description=description, duration_minutes=duration, price=price, deposit_amount=deposit)
        for name, description, duration, price, deposit in SERVICES
    ])


def remove_services(apps, schema_editor):
    Service = apps.get_model('booking', 'Service')
    Service.objects.filter(name__in=[service[0] for service in SERVICES]).delete()


class Migration(migrations.Migration):
    dependencies = [('booking', '0001_initial')]
    operations = [migrations.RunPython(create_services, remove_services)]
