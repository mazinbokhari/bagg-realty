# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realty_management', '0003_auto_20150329_2154'),
    ]

    operations = [
        migrations.AlterField(
            model_name='livesin',
            name='main_tenant',
            field=models.ForeignKey(to='realty_management.MainTenant'),
            preserve_default=True,
        ),
    ]
