# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='currency',
            name='symbol',
            field=models.CharField(help_text='If no symbol is entered, the 3 letter code will be used.', max_length=10, null=True, verbose_name='symbol', blank=True),
            preserve_default=True,
        ),
    ]
