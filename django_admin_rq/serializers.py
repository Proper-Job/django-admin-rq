# -*- coding: utf-8 -*-
from rest_framework import serializers

from django_admin_rq.models import JobStatus


class JobStatusSerializer(serializers.ModelSerializer):

    class Meta:
        model = JobStatus
