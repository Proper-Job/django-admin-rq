# Django Admin RQ
_________________


-   Setup django-rq according to documentation
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


-   Decorate your async tasks with the @job decorator.  They take the job_status object as their only argument

::

    from rq import get_current_job
    from django_rq import job
    from django_admin_rq.models import STATUS_STARTED
    
    @job
    def async_task(job_status):
        job = get_current_job()
        job_status.job_id = job.get_id()
        job_status.status = STATUS_STARTED
        job_status.save()

