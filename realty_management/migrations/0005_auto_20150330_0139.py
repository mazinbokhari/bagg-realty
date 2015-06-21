# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realty_management', '0004_auto_20150329_2156'),
    ]

    operations = [
        migrations.AddField(
            model_name='property',
            name='city',
            field=models.CharField(default='Champaign', max_length=800),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='property',
            name='state',
            field=models.CharField(default='IL', max_length=800),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='property',
            name='zip_code',
            field=models.CharField(default=61820, max_length=800),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='property',
            name='address',
            field=models.CharField(max_length=800),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='property',
            unique_together=set([('address', 'city', 'state', 'zip_code')]),
        ),
    ]
