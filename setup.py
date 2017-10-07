from setuptools import setup
from setuptools import find_packages

setup(
    name='tornado_mongo_rest',
    version='0.1.1',
    scripts=[
    ],
    packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires=[
        'django',
        'djangorestframework',
        'django-autofixture'
    ]
)
