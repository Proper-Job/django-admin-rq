# -*- coding: utf-8 -*-
from rest_framework.authentication import SessionAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from django_admin_rq.models import JobStatus
from django_admin_rq.serializers import JobStatusSerializer


class JobStatusView(APIView):
    authentication_classes = (SessionAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get(self, request, job_uuid=None, format=None):
        job_status = JobStatus.objects.get(job_uuid=job_uuid)
        return Response(JobStatusSerializer(job_status).data)
