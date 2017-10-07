# Django Remote Queryset [![Build Status](https://travis-ci.org/nicfix/django-remote-queryset.svg?branch=master)](https://travis-ci.org/nicfix/django-remote-queryset)

## Description

Django Remote Queryset (a.k.a. DRQ) is a library to execute rich ORM 
queries from client-side using the same interface of Django ORM.
 
## How it works

DRQ defines a JSON syntax to call all Django's Queryset methods.

Consider this example:


```python
    
    from myapp.models import MyModel
    
    not_null_title = MyModel.objects.filter(title__isnull=False)
   
```

DRQ query syntax for the previous filter is the following

```json
   {
       "_query_class" : "filter",
       "_condition" : "title__isnull",
       "_value" : false
   }
```

DRQ supports Django Rest Framework and automatically decodes and applies this filter to any GET request. 
 
## Installation

DRQ is distrubuted through pypi

```shell
   
   $ pip install django-remote-queryset
   
```

## Usage

1. Add **django_remote_queryset** to your INSTALLED_APPS:

```python    
    INSTALLED_APPS = [
        
        ...
        
        'rest_framework',
        'django_remote_queryset',
        
        ...
        
    ]
```

Django **rest_framework** is strongly recommended but if you prefer to use DRQ without it you can see [Advanced 
Usage](#advanced-usage) section.

2. Extend DRQModelViewSet for your model:

```python 
    from django_remote_queryset.viewset import DRQModelViewSet

    class MyModelModelViewSet(DRQModelViewSet):
        queryset = MyModel.objects.all()
        serializer_class = MyModelModelSerializer
```

And use it like any other Django REST Framework ViewSet!

3. Enjoy filtering from your browser!

```
   GET: http://yourdomain/my_model_rest_path/?query=
   
   query = {
       "_query_class" : "filter",
       "_condition" : "title__isnull",
       "_value" : false
   }
```

For further informations on DRF ViewSets see Django Rest Framework documentation.

## Example project

This repository contains a **example_django_project** folder.
Try it doing the following:


```bash

    $ cd example_django_app
    # Install site dependencies
    $ pip install -r requirements.txt
    # Create sqlite database
    $ python manage.py migrate
    # Create demo data
    $ python manage.py create_demo_data
    # Run the server
    $ python manage.py runserver
```

Then:
1. Go to **http://localhost:8000** and you should see the usual Django Rest Framework page.
2. Go to **http://localhost:8000/polls** and you should see the list of all polls available
3. Go to **http://localhost:8000/polls/?query={"_query_class":"filter","_condition":"title__icontains","_value":"DRQ"}**



## Advanced Usage

It's possible to extend/customize DRQ using it in your extisting ViewSets or integrating it in your own custom 
Views/Django code. 

### Use the DRQFilterBackend

DRQ is implemented using DRF's **filter_backends**, you can add it to your ModelViewSet easily


```python 
    from django_remote_queryset.backend import DRQFilterBackend

    class AnotherModelViewSet(ModelViewSet):
        filter_backends = ( ..., DRQFilterBackend, ...)
```

### Use the QueryDecoder

You can use directly the QueryDecoder to decode and apply the json_query to any queryset


```python 
    from django_remote_queryset.queries import QueryDecoder
    
    ...

    original_queryset = MyModel.objects.all()
    
    
    json_query = {
       "_query_class" : "filter",
       "_condition" : "title__isnull",
       "_value" : false
   }
    
    query = QueryDecoder \
            .decodeJSONQuery(json_query)
    
    if query is not None:
        filtered_queryset = query.applyOnQuerySet(original_queryset)
```

## DRQ JSON Syntax Specification

DRQ Queries are built using the Composite Pattern. Several queries are already available and the Framework could be 
extended with custom ones.
All the queries are contained in **django_remote_queryset.queries** module.


### Query
This is the abstract one, defines the interface for every child.

```python 
    class Query():
        def __init__(self, json_query):
            """
            Initializes the sub_tree of this query starting from the json_query parameter
            :param json_query: dict
            """
            pass
        
        def applyOnQuerySet(self, queryset):
            """
            Applies the sub_tree of this query to the queryset passed as parameter
            :param queryset: Queryset
            :return: Queryset
            """
            return queryset 
```

It's JSON syntax is the following

```json
    {
      "_query_class":"query"
    }
```

### Filter

This query applies the .filter( ... ) method on the queryset

It's JSON syntax is the following

```json
    {
      "_query_class": "filter",
      "_condition": [string] | string,
      "_value": [*] | * 
    }
```

Examples:

1. Single lookup

```python
    
    Person.filter(age__gte=4)
```

```json
    {
      "_query_class": "filter",
      "_condition": "age__gte",
      "_value": 4 
    }
```

2. Multiple lookups

```python
    
    Person.filter(age__gte=4, name__icontains='Nic')
```

```json
    {
      "_query_class": "filter",
      "_condition": ["age__gte","name__icontains"],
      "_value": [4,"Nic"] 
    }
```

### Exclude

This query applies the .exclude( ... ) method on the queryset

It's JSON syntax is the following

```json
    {
      "_query_class": "exclude",
      "_condition": [string] | string,
      "_value": [*] | * 
    }
```

Examples:

1. Single lookup

```python
    
    Person.exclude(age__gte=4)
```

```json
    {
      "_query_class": "exclude",
      "_condition": "age__gte",
      "_value": 4 
    }
```

2. Multiple lookups

```python
    
    Person.exclude(age__gte=4, name__icontains='Nic')
```

```json
    {
      "_query_class": "exclude",
      "_condition": ["age__gte","name__icontains"],
      "_value": [4,"Nic"] 
    }
```

### CompositeQuery
This query creates a chain of subqueries applying all it's sub_tree on the queryset.

It's JSON syntax is the following

```json
    {
      "_query_class": "compositequery",
      "_sub_queries":[
        ... other queries ...
      ]
    }
```

The subqueries are applied as a chain.

```python
    for query in self._sub_queries:
        queryset = query.applyOnQuerySet(queryset)
```

Examples:

1. Chained filters

```python
    Person.objects.filter(age__gte=4).filter(name__icontains='Nic')
```

```json
    {
      "_query_class": "compositequery",
      "_sub_queries":[
        {
            "_query_class": "filter",
            "_condition": "age__gte",
            "_value": 4 
        },
        {
            "_query_class": "filter",
            "_condition": "name__icontains",
            "_value": "Nic"
        }
      ]
    }
```

2. Chained mixed queries

```python
    Person.objects.filter(age__gte=4).exclude(name__icontains='Nic')
```

```json
    {
      "_query_class": "compositequery",
      "_sub_queries":[
        {
            "_query_class": "filter",
            "_condition": "age__gte",
            "_value": 4 
        },
        {
            "_query_class": "exclude",
            "_condition": "name__icontains",
            "_value": "Nic"
        }
      ]
    }
```