from setuptools import setup
from setuptools import find_packages

setup(
    name='django_remote_queryset',
    version='0.1.3',
    scripts=[
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        'django',
        'djangorestframework',
        'django-autofixture'
    ]
)
