import os
from setuptools import setup, find_packages

README = open(os.path.join(os.path.dirname(__file__), 'README.md')).read()

# allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-admin-rq',
    version='0.1.3',
    packages=find_packages(),
    include_package_data=True,
    license='MIT License',
    description="Django admin rq is a django package that creates a 4 step (form, preview, main, complete) asynchronous workflow from a ModelAdmin's changelist or changeform.",
    long_description=README,
    url='https://github.com/Proper-Job/django-admin-rq',
    author='Moritz Pfeiffer',
    author_email='moritz.pfeiffer@alp-phone.ch',
    zip_safe=False,
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: Web Environment',
        'Framework :: Django',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
    install_requires=['django-rq >= 0.9.0', 'django>=1.8', 'djangorestframework>=3.3.0']
)
