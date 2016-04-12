from functools import update_wrapper

import re

import django_rq
from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ImproperlyConfigured
from django.core.management import call_command
from django.core.urlresolvers import reverse
from django.db import transaction
from django.db.models import Model
from django.forms import ModelForm
from django.http import HttpResponseRedirect
from django.template import RequestContext
from django.template.response import TemplateResponse
from django.utils.decorators import method_decorator
from django.utils.translation import ugettext_lazy as _
from django.contrib import admin
from django.views.decorators.csrf import csrf_protect
from django.utils import six

from django_admin_rq.models import JobStatus

csrf_protect_m = method_decorator(csrf_protect)


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
                r'^job/(?P<job_name>[a-zA-Z-_]+)/preview/(?P<object_id>\d{1,10})?$',
                wrap(self.job_preview),
                name='%s_%s_job_preview' % info
            ),
            url(
                r'^job/(?P<job_name>[a-zA-Z-_]+)/run/(?P<object_id>\d{1,10})?$',
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

    def get_job_preview_template(self, job_name):
        """
        Returns the template for this job's preview page
        """
        return 'django_admin_rq/job_preview.html'

    def get_job_run_template(self, job_name):
        """
        Returns the template for this job's run page
        """
        return 'django_admin_rq/job_run.html'

    def get_job_complete_template(self, job_name):
        """
        Returns the template for this job's complete page
        """
        return 'django_admin_rq/job_complete.html'

    def get_preview_job_callable(self, job_name):
        """
        Returns the function decorated with :func:`~django_rq.job` that runs the preview async job.
        """
        return None

    def get_run_job_callable(self, job_name):
        """
        Returns the function decorated with :func:`~django_rq.job` that runs the main async job.
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

    def serialize_job_form(self, form, job_name):
        """
        Given this job's bound form return the form's data as a session serializable object
        The field order is preserved from the original form
        """
        data = []
        for field_name, field in form.fields.items():
            if field_name in form.cleaned_data:
                form_value = form.cleaned_data[field_name]
                if isinstance(form_value, Model):
                    ctype = ContentType.objects.get_for_model(form_value)
                    form_value = 'contenttype:{0}.{1}:{2}'.format(
                        ctype.app_label,
                        ctype.model,
                        form_value.pk
                    )
                data.append({
                    'name': field_name,
                    'label': field.label,
                    'value': form_value,
                })
        return data

    def get_job_session_data(self, request, job_name):
        return request.session.get(self._get_job_session_key(job_name), {})

    def set_job_session_data(self, request, job_name, session_data):
        request.session[self._get_job_session_key(job_name)] = session_data

    def get_job_form_data(self, request, job_name):
        form_data = []
        session_data = self.get_job_session_data(request, job_name)
        if 'form_data' in session_data:
            for field_data in session_data['form_data']:
                value = field_data['value']
                if isinstance(value, six.string_types) and value.startswith('contenttype:'):
                    match = re.search('contenttype:([a-zA-Z]+)\.([a-zA-Z]+):(\d{1,10})', value)
                    if match:
                        field_data['value'] = ContentType.objects.get(
                            app_label=match.group(1),
                            model=match.group(2)
                        ).get_object_for_this_type(**{
                            'pk': match.group(3)
                        })
                form_data.append(field_data)
        return form_data

    def get_job_context(self, request, job_name, object_id, view_name=None):
        request.current_app = self.admin_site.name
        context = dict(
            self.admin_site.each_context(request),
            opts=self.model._meta,
            app_label=self.model._meta.app_label,
            title=self.get_job_title(job_name),
            job_name=job_name,
        )
        if object_id:
            try:
                obj = self.model.objects.get(pk=object_id)
                context['original'] = obj
            except:
                pass
        context['job_data'] = self.get_job_form_data(request, job_name)
        return context

    def get_job_status_url(self, job_uuid):
        return reverse('admin-rq-job-status', kwargs={'job_uuid': job_uuid})

    def job_start(self, request, job_name='', object_id=None):
        context = self.get_job_context(request, job_name, object_id, view_name='start')
        info = self.model._meta.app_label, self.model._meta.model_name

        if request.method == 'GET':
            form = self.get_job_form_class(job_name)(initial=self.get_job_form_initial(request, job_name))
        else:
            form = self.get_job_form_class(job_name)(request.POST, request.FILES)
            if form.is_valid():
                job_session_data = {}
                job_session_data['form_data'] = self.serialize_job_form(form, job_name)
                self.set_job_session_data(request, job_name, job_session_data)
                url_kwargs = {
                    'job_name': job_name
                }
                if object_id:
                    url_kwargs['object_id'] = object_id
                return HttpResponseRedirect(
                    reverse(
                        'admin:%s_%s_job_preview' % info,
                        kwargs=url_kwargs,
                        current_app=self.admin_site.name
                    )
                )
        context['form'] = form
        return TemplateResponse(request, self.get_job_start_template(job_name), RequestContext(request, context))

    def job_preview(self, request, job_name='', object_id=None):
        context = self.get_job_context(request, job_name, object_id, view_name='preview')
        job_session_data = self.get_job_session_data(request, job_name)

        if 'job_uuid' in job_session_data:
            job_status = JobStatus.objects.get(job_uuid=job_session_data['job_uuid'])
            context['job_status'] = job_status.status
        else:
            job_callable = self.get_preview_job_callable(job_name)
            if callable(job_callable):
                job_status = JobStatus()
                job_status.save()
                job_callable.delay(job_status)

                context['job_running'] = True
                context['job_status_url'] = self.get_job_status_url(job_status.job_uuid)

                job_session_data['job_uuid'] = job_status.job_uuid
                self.set_job_session_data(request, job_name, job_session_data)
            else:
                raise ImproperlyConfigured('{}.{} must return a callable'.format(self.__class__.__name__, self.get_preview_job_callable.__name__))
        return TemplateResponse(request, self.get_job_preview_template(job_name), RequestContext(request, context))

    def job_run(self, request, job_name='', object_id=None):
        context = self.get_job_context(request, job_name, object_id, view_name='run')
        return TemplateResponse(request, self.get_job_run_template(job_name), RequestContext(request, context))

    def job_complete(self, request, job_name='', object_id=None):
        context = self.get_job_context(request, job_name, object_id, view_name='complete')
        return TemplateResponse(request, self.get_job_complete_template(job_name), RequestContext(request, context))
