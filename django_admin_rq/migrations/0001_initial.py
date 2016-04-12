# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='JobStatus',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, auto_created=True, verbose_name='ID')),
                ('created_on', models.DateTimeField(auto_now_add=True)),
                ('progress', models.PositiveIntegerField(default=0)),
                ('progress_type', models.CharField(choices=[('indeterminate', 'Indeterminate'), ('determinate', 'Determinate')], max_length=50, default='indeterminate')),
                ('job_id', models.CharField(max_length=255, default='')),
                ('job_uuid', models.CharField(max_length=255, default='caea5eae5c2a41ca81e10a11c8f4f31b')),
                ('status', models.CharField(choices=[('QUEUED', 'Queued'), ('STARTED', 'Started'), ('FINISHED', 'Finished'), ('FAILED', 'Failed')], max_length=128, default='QUEUED')),
                ('failure_reason', models.TextField(default='')),
            ],
            options={
                'verbose_name_plural': 'Job statuses',
                'ordering': ('-created_on',),
                'verbose_name': 'Job status',
            },
        ),
    ]
