# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('realty_management', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='supports',
            name='vendor',
            field=models.ForeignKey(to='realty_management.Vendor'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='supports',
            unique_together=set([('vendor', 'property', 'service')]),
        ),
    ]
