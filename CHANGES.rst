Changelog for Django admin rq
=============================

0.2.0 (2017-11-02)
------------------

BREAKING CHANGES
================

Classes inheriting from JobAdminMixin need to make changes to the methods listed below.

- The following methods of JobAdminMixin received extra kwargs:
    - get_job_form_class
    - get_job_form_initial
    - get_job_form_template
    - get_job_run_template
    - get_job_complete_template
    - get_job_callable
    - get_job_media


0.1.5 (2017-03-28)
------------------

- Added fields = '__all__' to JobStatusSerializer to allow with newer DRF versions.


0.1.4 (2017-03-16)
------------------

- Added Django 1.10 support.


0.1.3 (2016-12-20)
------------------

- The form template learned to output hidden fields without a form-row wrapper.


0.1.2 (2016-12-20)
------------------

- Added form_data block to run template that allows overriding form data.


0.1.1 (2016-04-26)
------------------

- Fixed session key string format error.
- Workflow can start on either form, preview or main views.



0.1.0 (2016-04-20)
------------------

- Initial release.
