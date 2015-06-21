# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import phonenumber_field.modelfields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='LivesIn',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('lease_start', models.DateTimeField()),
                ('lease_end', models.DateTimeField()),
                ('lease_copy', models.FileField(upload_to=b'')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='MainTenant',
            fields=[
                ('ssn', models.PositiveIntegerField(serialize=False, primary_key=True, validators=[django.core.validators.MaxValueValidator(999999999), django.core.validators.MinValueValidator(100000000)])),
                ('name', models.CharField(max_length=500)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(max_length=128)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Property',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('address', models.CharField(unique=True, max_length=800)),
                ('owner', models.CharField(max_length=500)),
                ('num_units', models.IntegerField()),
                ('mortgage', models.FileField(null=True, upload_to=b'', blank=True)),
                ('image', models.FileField(null=True, upload_to=b'', blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Supports',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('service', models.CharField(max_length=500)),
                ('monthly_rate', models.IntegerField()),
                ('property', models.ForeignKey(to='realty_management.Property')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Unit',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('number', models.CharField(max_length=800)),
                ('rent', models.IntegerField()),
                ('sq_ft', models.IntegerField()),
                ('num_baths', models.IntegerField()),
                ('num_bed', models.IntegerField()),
                ('property', models.ForeignKey(to='realty_management.Property')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Vendor',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('phone', phonenumber_field.modelfields.PhoneNumberField(unique=True, max_length=128)),
                ('company_name', models.CharField(max_length=500)),
                ('address', models.CharField(max_length=800)),
                ('contact_name', models.CharField(max_length=500)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AlterUniqueTogether(
            name='unit',
            unique_together=set([('number', 'property')]),
        ),
        migrations.AddField(
            model_name='supports',
            name='vendor',
            field=models.ForeignKey(to='realty_management.Vendor', unique=True),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='supports',
            unique_together=set([('vendor', 'property')]),
        ),
        migrations.AddField(
            model_name='livesin',
            name='main_tenant',
            field=models.ForeignKey(to='realty_management.MainTenant', unique=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='livesin',
            name='unit_number',
            field=models.ForeignKey(to='realty_management.Unit'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='livesin',
            unique_together=set([('main_tenant', 'unit_number')]),
        ),
    ]
