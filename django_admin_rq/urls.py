# -*- coding: utf-8 -*-
from django.conf.urls import url
from django_admin_rq import views

urlpatterns = [
    url(r'^job/status/(?P<job_uuid>[a-zA-Z0-9-_]+)/', views.JobStatusView.as_view(), name='admin-rq-job-status'),
]
