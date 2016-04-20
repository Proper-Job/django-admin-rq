# Django Admin RQ

Django admin rq is a django package that creates a 4 step (form, preview, main, complete) asynchronous workflow from a ModelAdmin's changelist or changeform.
By using the JobAdminMixin class in your ModelAdmin subclass you can define and run jobs by overriding appropriate inherited methods.
It builds upon [django-rq][django-rq].

[django-rq]: https://github.com/ui/django-rq

# Installation

-   Setup django-rq according to documentation
-   ``pip install django-admin-rq``
-   Add ``django_admin_rq`` to your ``INSTALLED_APPS``
-   Add django-admin-rq.urls to your url config

::

    url(r'^django-admin-rq/', include('django_admin_rq.urls')),


-   Add custom execption handler to queues: ```settings.py```

::

    RQ_QUEUES = {
        'default': {
            'HOST': 'localhost',
            'PORT': 6379,
            'DB': 0,
            'DEFAULT_TIMEOUT': 360,
        }
    }
    RQ = {
        'EXCEPTION_HANDLERS': ['django_admin_rq.exceptions.exception_handler']
    }


-   Decorate your async tasks with the @job decorator.  
-   They take the three arguments all of which need to be pickleable:
    -   An instance of django_admin_rq.models.JobStatus
    -   The form data from step 1
    -   An extra context object you provide if necessary

::

    from rq import get_current_job
    from django_rq import job
    
    @job
    def async_task(job_status, form_data, extra_context):
        job = get_current_job()
        job_status.set_job_id(job.get_id())
        job_status.start()
        
        ... do your job
        
        job_status.finish()

