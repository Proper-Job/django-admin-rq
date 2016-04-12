# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_admin_rq.models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JobStatus',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('progress', models.PositiveIntegerField(default=0)),
                ('job_id', models.CharField(max_length=255, default='')),
                ('job_uuid', models.CharField(max_length=255, default=django_admin_rq.models._get_uuid)),
                ('status', models.CharField(choices=[('QUEUED', 'Queued'), ('STARTED', 'Started'), ('FINISHED', 'Finished'), ('FAILED', 'Failed')], default='QUEUED', max_length=128)),
                ('failure_reason', models.TextField(default='')),
            ],
            options={
                'verbose_name_plural': 'Job statuses',
                'verbose_name': 'Job status',
                'ordering': ('-created_on',),
            },
        ),
    ]
