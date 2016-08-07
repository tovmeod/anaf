# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import time


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='token',
            name='timestamp',
            field=models.IntegerField(default=time.time),
            preserve_default=True,
        ),
    ]
