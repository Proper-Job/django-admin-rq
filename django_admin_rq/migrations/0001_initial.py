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
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('progress', models.PositiveIntegerField(default=0)),
                ('job_id', models.CharField(max_length=255, default='')),
                ('job_uuid', models.CharField(max_length=255, default=django_admin_rq.models._get_uuid)),
                ('status', models.CharField(max_length=128, default='QUEUED', choices=[('QUEUED', 'Queued'), ('STARTED', 'Started'), ('FINISHED', 'Finished'), ('FAILED', 'Failed')])),
                ('result', models.TextField(default='')),
                ('failure_reason', models.TextField(default='')),
            ],
            options={
                'verbose_name': 'Job status',
                'verbose_name_plural': 'Job statuses',
                'ordering': ('-created_on',),
            },
        ),
    ]
