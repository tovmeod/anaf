from __future__ import unicode_literals

from django.db import migrations

contact_types = ('Person', 'Company', 'Department')


def _add_data(ContactType):
    for name in contact_types:
        ContactType.objects.get_or_create({'name': name})


def add_data(apps, schema_editor):
    ContactType = apps.get_model('identities', 'ContactType')
    _add_data(ContactType)


class Migration(migrations.Migration):

    dependencies = [
        ('identities', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_data),
    ]