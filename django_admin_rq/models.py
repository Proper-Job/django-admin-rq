# -*- coding: utf-8 -*-
from __future__ import unicode_literals

import uuid

from django.db import models
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


@python_2_unicode_compatible
class JobStatus(models.Model):
    """
    A model to save information about an asynchronous job
    """
    created_on = models.DateTimeField(auto_now_add=True)
    progress = models.PositiveIntegerField(default=0)
    job_id = models.CharField(max_length=255, default='')
    job_uuid = models.CharField(max_length=255, default=uuid.uuid4().hex)
    status = models.CharField(max_length=128, choices=STATUS_CHOICES, default=STATUS_QUEUED)
    failure_reason = models.TextField(default='')

    def __str__(self):
        return self.job_uuid

    def start(self, save=True):
        self.status = STATUS_STARTED
        if save:
            self.save(update_fields=['status'])

    def finish(self, save=True):
        self.status = STATUS_FINISHED
        if save:
            self.save(update_fields=['status'])

    class Meta:
        ordering = ('-created_on', )
        verbose_name = _('Job status')
        verbose_name_plural = _('Job statuses')
