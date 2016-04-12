# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('django_admin_rq', '0001_initial'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='jobstatus',
            name='progress_type',
        ),
        migrations.AlterField(
            model_name='jobstatus',
            name='job_uuid',
            field=models.CharField(max_length=255, default='2741712f93f64f8c9f373f056bf582cd'),
        ),
    ]
