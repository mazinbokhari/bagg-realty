# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realty_management', '0002_auto_20150328_0104'),
    ]

    operations = [
        migrations.AlterUniqueTogether(
            name='livesin',
            unique_together=set([('main_tenant', 'unit_number', 'lease_end')]),
        ),
    ]
