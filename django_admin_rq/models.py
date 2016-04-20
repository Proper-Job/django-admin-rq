# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.core.urlresolvers import reverse
from django.db import models
from django.utils import six
from django.utils.six import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _


STATUS_QUEUED = 'QUEUED'
STATUS_STARTED = 'STARTED'
STATUS_FINISHED = 'FINISHED'
STATUS_FAILED = 'FAILED'

STATUS_CHOICES = (
    (STATUS_QUEUED, _('Queued')),
    (STATUS_STARTED, _('Started')),
    (STATUS_FINISHED, _('Finished')),
    (STATUS_FAILED, _('Failed')),
)


def _get_uuid():
    return uuid.uuid4().hex


@python_2_unicode_compatible
class JobStatus(models.Model):
    """
    A model to save information about an asynchronous job
    """
    created_on = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0)
    job_id = models.CharField(max_length=255, default='')
    job_uuid = models.CharField(max_length=255, default=_get_uuid)
    status = models.CharField(max_length=128, choices=STATUS_CHOICES, default=STATUS_QUEUED)
    result = models.TextField(default='')
    failure_reason = models.TextField(default='')

    def __str__(self):
        return self.job_uuid

    def url(self):
        return reverse('admin-rq-job-status', kwargs={'job_uuid': self.job_uuid})

    def start(self, save=True):
        self.status = STATUS_STARTED
        if save:
            self.save()

    def finish(self, save=True):
        self.status = STATUS_FINISHED
        if save:
            self.save()

    def fail(self, save=True):
        self.status = STATUS_FAILED
        if save:
            self.save()

    def set_job_id(self, job_id, save=True):
        self.job_id = job_id
        if save:
            self.save()

    def set_result(self, result, save=True):
        if isinstance(result, six.string_types):
            self.result = result
            if save:
                self.save()
        else:
            raise ValueError('Result must be a string type.')

    def set_progress(self, progress, save=True):
        self.progress = int(progress)
        if save:
            self.save()

    def is_queued(self):
        return self.status == STATUS_QUEUED

    def is_started(self):
        return self.status == STATUS_STARTED

    def is_finished(self):
        return self.status == STATUS_FINISHED

    def is_failed(self):
        return self.status == STATUS_FAILED

    class Meta:
        ordering = ('-created_on', )
        verbose_name = _('Job status')
        verbose_name_plural = _('Job statuses')
