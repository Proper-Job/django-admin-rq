# -*- coding: utf-8 -*-
import re
import copy
from collections import OrderedDict
from functools import update_wrapper

from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db import models
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.utils import six
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_protect

from django_admin_rq.models import JobStatus
from django.utils.encoding import force_text

csrf_protect_m = method_decorator(csrf_protect)

_CONTENT_TYPE_PREFIX = 'contenttype:'
_CONTENT_TYPE_RE_PATTERN = 'contenttype:([a-zA-Z-_]+)\.([a-zA-Z]+):(\d{1,10})'

START_VIEW = 'start'
PREVIEW_VIEW = 'preview'
MAIN_VIEW = 'main'
COMPLETE_VIEW = 'complete'


class JobAdminMixin(object):

    def get_urls(self):
        from django.conf.urls import url
        urls = super(JobAdminMixin, self).get_urls()
        info = self.model._meta.app_label, self.model._meta.model_name

        def wrap(view):
            def wrapper(*args, **kwargs):
                return self.admin_site.admin_view(view)(*args, **kwargs)

            return update_wrapper(wrapper, view)

        job_urls = [
            url(
                r'^job/(?P<job_name>[a-zA-Z-_]+)/start/(?P<object_id>\d{1,10})?$',
                wrap(self.job_start),
                name='%s_%s_job_start' % info
            ),
            url(
                r'^job/(?P<job_name>[a-zA-Z-_]+)/(?P<view_name>(preview|main))/(?P<object_id>\d{1,10})?$',
                wrap(self.job_run),
                name='%s_%s_job_run' % info
            ),
            url(
                r'^job/(?P<job_name>[a-zA-Z-_]+)/complete/(?P<object_id>\d{1,10})?$',
                wrap(self.job_complete),
                name='%s_%s_job_complete' % info
            ),
        ]
        return job_urls + urls

    def get_job_names(self):
        """
        Returns an iterable of strings that represent all the asyncronous jobs this ModelAdmin can handle.
        These names act as identifying attributes and are not user visible.
        :func:`~django_admin_rq.admin.JobAdminMixin.get_job_titles` returns the user visible portion for these identifiers.
        """
        return []

    def get_job_form_class(self, job_name):
        """
        Returns the form class for this job's start page.
        """
        return None

    def get_job_form_initial(self, request, job_name):
        """
        Returns the job form's initial data for this job's start page.
        """
        return {}

    def get_job_title(self, job_name):
        """
        Returns the user visible title for this job identified by job_name
        """
        return ''

    def get_changelist_link_css(self, job_name):
        """
        Returns an iterable of css classes which are added to the changelist link that points to the job's start page
        """
        return ['addlink']

    def get_changeform_link_css(self, job_name):
        """
        Returns an iterable of css classes which are added to the changeform link that points to the job's start page
        """
        return ['addlink']

    def show_job_on_changelist(self, job_name):
        """
        Returns boolean whether or not this job should be shown on the changelist
        """
        return True

    def show_job_on_changeform(self, job_name):
        """
        Returns boolean whether or not this job should be shown on the changeform
        """
        return True

    def get_job_start_template(self, job_name):
        """
        Returns the template for this job's start page
        """
        return 'django_admin_rq/job_start.html'

    def get_job_run_template(self, job_name, preview=True):
        """
        Returns the template for this job's run page.
        """
        return 'django_admin_rq/job_run.html'

    def get_job_complete_template(self, job_name):
        """
        Returns the template for this job's complete page
        """
        return 'django_admin_rq/job_complete.html'

    def get_job_callable(self, job_name, preview=True):
        """
        Returns the function decorated with :func:`~django_rq.job` that runs the run async job for this view.
        view_name is either 'preview' or 'main'
        """
        return None

    def get_preview_queue(self, job_name):
        """
        Returns the queue name for the preview job
        """
        return 'default'

    def get_run_queue(self, job_name):
        """
        Returns the queue name for the main job
        """
        return 'default'

    def _get_job_session_key(self, job_name):
        return 'django_admin_rq_'.format(job_name)

    @csrf_protect_m
    def changelist_view(self, request, extra_context=None):
        if extra_context is None:
            extra_context = {}

        info = self.model._meta.app_label, self.model._meta.model_name
        jobs = []
        for job_name in self.get_job_names():
            if self.show_job_on_changelist(job_name):
                url_kwargs = {
                    'job_name': job_name,
                }
                jobs.append({
                    'title': self.get_job_title(job_name),
                    'url': reverse('admin:%s_%s_job_start' % info, kwargs=url_kwargs, current_app=self.admin_site.name),
                    'css': ' '.join(self.get_changelist_link_css(job_name))
                })
        extra_context.update({
            'changelist_jobs': jobs
        })
        return super(JobAdminMixin, self).changelist_view(request, extra_context)

    @csrf_protect_m
    @transaction.atomic
    def changeform_view(self, request, object_id=None, form_url='', extra_context=None):
        if extra_context is None:
            extra_context = {}

        info = self.model._meta.app_label, self.model._meta.model_name
        jobs = []
        for job_name in self.get_job_names():
            if self.show_job_on_changeform(job_name) and object_id:
                url_kwargs = {
                    'job_name': job_name,
                    'object_id': object_id,
                }
                jobs.append({
                    'title': self.get_job_title(job_name),
                    'url': reverse('admin:%s_%s_job_start' % info, kwargs=url_kwargs, current_app=self.admin_site.name),
                    'css': ' '.join(self.get_changeform_link_css(job_name))
                })
        extra_context.update({
            'changeform_jobs': jobs
        })
        return super(JobAdminMixin, self).changeform_view(request, object_id=object_id, form_url=form_url, extra_context=extra_context)

    def serialize_form(self, form):
        """
        Given this job's bound form return the form's data as a session serializable object
        The field order is preserved from the original form
        """
        data = []
        for field_name, field in form.fields.items():
            if field_name in form.cleaned_data:
                form_value = form.cleaned_data[field_name]
                if isinstance(form_value, models.Model):
                    ctype = ContentType.objects.get_for_model(form_value)
                    form_value = '{0}{1}.{2}:{3}'.format(
                        _CONTENT_TYPE_PREFIX,
                        ctype.app_label,
                        ctype.model,
                        form_value.pk
                    )
                data.append({
                    'name': field_name,
                    'label': force_text(field.label),
                    'value': form_value,
                })
        return data

    def get_session_data(self, request, job_name):
        return request.session.get(self._get_job_session_key(job_name), {})

    def get_session_form_data(self, request, job_name):
        """
        Retrieve form data that was serialized to the session in :func:`~django_admin_rq.admin.JobAdminMixin.job_start`
        Values prefixed with 'contenttype:' are replace with the instantiated Model versions.
        """
        form_data = []
        serialized_data = self.get_session_data(request, job_name).get('form_data', [])

        for field_data in copy.deepcopy(serialized_data):  # Don't modify the serialized session data
            value = field_data['value']
            if isinstance(value, six.string_types) and value.startswith(_CONTENT_TYPE_PREFIX):
                match = re.search(_CONTENT_TYPE_RE_PATTERN, value)
                if match:
                    field_data['value'] = ContentType.objects.get(
                        app_label=match.group(1),
                        model=match.group(2)
                    ).get_object_for_this_type(**{
                        'pk': match.group(3)
                    })
            form_data.append(field_data)

        return form_data

    def get_session_form_data_as_dict(self, request, job_name):
        """
        Convenience method to have the form data like form.cleaned_data
        """
        data_dict = OrderedDict()
        for value_dict in self.get_session_form_data(request, job_name):
            data_dict[value_dict['name']] = value_dict['value']
        return data_dict

    def set_session_job_status(self, request, job_name, job_status, view_name):
        """
        Serializes the given :class:`~django_admin_rq.models.JobStatus` to this job's session.
        """
        if isinstance(job_status, JobStatus) and job_status.pk:
            ctype = ContentType.objects.get_for_model(job_status)
            status = '{0}{1}.{2}:{3}'.format(_CONTENT_TYPE_PREFIX, ctype.app_label, ctype.model, job_status.pk)
            session_data = self.get_session_data(request, job_name)
            session_data['{}_job_status'.format(view_name)] = status
            request.session.modified = True
        else:
            raise ValueError('job_status must be an instance of {} that has a valid pk.'.format(JobStatus.__class__.__name__))

    def get_session_job_status(self, request, job_name, view_name):
        """
        Returns an instance of :class:`~django_admin_rq.models.JobStatus` representing the status for the given view.
        Returns None if the reference is missing from the session.
        """
        session_data = self.get_session_data(request, job_name)
        status = session_data.get('{}_job_status'.format(view_name), None)
        if status is not None and isinstance(status, six.string_types) and status.startswith(_CONTENT_TYPE_PREFIX):
            match = re.search(_CONTENT_TYPE_RE_PATTERN, status)
            if match:
                return ContentType.objects.get(
                    app_label=match.group(1),
                    model=match.group(2)
                ).get_object_for_this_type(**{
                    'pk': match.group(3)
                })
        return None

    def get_job_context(self, request, job_name, object_id, view_name):
        """
        Returns the context for all django-admin-rq view (start|preview|main|complete)
        """
        request.current_app = self.admin_site.name
        context = dict(
            self.admin_site.each_context(request),
            opts=self.model._meta,
            app_label=self.model._meta.app_label,
            title=self.get_job_title(job_name),
            job_name=job_name,
            view_name=view_name,
            start_view=START_VIEW,
            preview_view=PREVIEW_VIEW,
            main_view=MAIN_VIEW,
            complete_view=COMPLETE_VIEW,
            job_form_data=self.get_session_form_data(request, job_name),
            preview=view_name == PREVIEW_VIEW
        )
        if object_id:
            try:
                obj = self.model.objects.get(pk=object_id)
                context['original'] = obj
            except:
                pass
        return context

    def job_start(self, request, job_name='', object_id=None):
        context = self.get_job_context(request, job_name, object_id, START_VIEW)
        info = self.model._meta.app_label, self.model._meta.model_name

        if request.method == 'GET':
            form = self.get_job_form_class(job_name)(initial=self.get_job_form_initial(request, job_name))
        else:
            form = self.get_job_form_class(job_name)(request.POST, request.FILES)
            if form.is_valid():
                # Save the serialized form data to the session
                session_data = {}
                session_data['form_data'] = self.serialize_form(form)
                request.session[self._get_job_session_key(job_name)] = session_data

                url_kwargs = {
                    'job_name': job_name,
                    'view_name': PREVIEW_VIEW,
                }
                if object_id:
                    url_kwargs['object_id'] = object_id
                return HttpResponseRedirect(
                    reverse(
                        'admin:%s_%s_job_run' % info,
                        kwargs=url_kwargs,
                        current_app=self.admin_site.name
                    )
                )
        context['form'] = form
        return TemplateResponse(request, self.get_job_start_template(job_name), RequestContext(request, context))

    def job_run(self, request, job_name='', object_id=None, view_name=PREVIEW_VIEW):
        context = self.get_job_context(request, job_name, object_id, view_name)
        preview = view_name == PREVIEW_VIEW

        # job_status is None when no job has been started
        job_status = self.get_session_job_status(request, job_name, view_name)
        if job_status is None:
            job_callable = self.get_job_callable(job_name, preview=preview)
            if callable(job_callable):
                job_status = JobStatus()
                job_status.save()
                self.set_session_job_status(request, job_name, job_status, view_name)
                context['job_status'] = job_status
                context['job_status_url'] = job_status.url()  # The frontend starts polling the status url if it's present
                job_callable.delay(job_status, self.get_session_form_data_as_dict(request, job_name))
        else:
            context['job_status'] = job_status
        return TemplateResponse(request, self.get_job_run_template(job_name, preview=preview), RequestContext(request, context))

    def job_complete(self, request, job_name='', object_id=None):
        context = self.get_job_context(request, job_name, object_id, COMPLETE_VIEW)
        return TemplateResponse(request, self.get_job_complete_template(job_name), RequestContext(request, context))
