# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import traceback

from django_rq import get_failed_queue

from django_admin_rq.models import JobStatus, STATUS_FAILED


def exception_handler(job, *exc_info):
    try:
        job_status = JobStatus.objects.get(job_id=job.get_id())
        job_status.status = STATUS_FAILED
        job_status.save(update_fields=['status'])
    except:
        pass

    fq = get_failed_queue()
    exc_string = ''.join(traceback.format_exception(*exc_info))
    fq.quarantine(job, exc_info=exc_string)
