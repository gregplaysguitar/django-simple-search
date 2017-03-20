Django simple search provides the same functionality and convenience as
`search_fields` does in the django admin.

See <http://gregbrown.co.nz/code/django-simple-search/> for more details.

[![Circle CI](https://circleci.com/gh/gregplaysguitar/django-simple-search.svg?style=svg)](https://circleci.com/gh/gregplaysguitar/django-simple-search)
[![codecov](https://codecov.io/gh/gregplaysguitar/django-simple-search/branch/master/graph/badge.svg)](https://codecov.io/gh/gregplaysguitar/django-simple-search)
[![Latest Version](https://img.shields.io/pypi/v/django-simple-search.svg?style=flat)](https://pypi.python.org/pypi/django-simple-search/)


## Installation

Download the source from https://pypi.python.org/pypi/django-simple-search/
and run `python setup.py install`, or:

    > pip install django-simple-search

Django 1.8 or higher is required.


## Quick start

    from simple_search import search_filter
    from .models import MyModel

    query = 'test'
    search_fields = ['^title', 'description', '=id']
    f = search_filter(search_fields, query)
    filtered = MyModel.objects.filter(f)

For convenience you can create a search form class via the provided factory:

    from .models import MyModel
    from simple_search import search_form_factory

    SearchForm = search_form_factory(MyModel.objects.all(),
                                     ['^title', 'description'])


## Reference

#### `simple_search.search_filter(search_fields, query)`

Given a list of `search_fields` to search on and a query, return a `models.Q`
object which can be used to filter a queryset.

`search_fields` behaves exactly like the django admin
[`search_fields`](https://docs.djangoproject.com/en/1.10/ref/contrib/admin/#django.contrib.admin.ModelAdmin.search_fields)
option. Example:

    search_fields = [
        # match from the start of the title field
        '^title',

        # match anywhere within the description field
        'description',

        # match from the start of the related category's title field
        '^category__title',

        # exact match on object id
        '=id'
    ]


#### `simple_search.search_form_factory(queryset, search_fields)`

Create a search form class which will filter `queryset` according to
`search_fields` and the form field `q`. Example:

    # forms.py
    from .models import MyModel
    from simple_search import search_form_factory

    SearchForm = search_form_factory(MyModel.objects.all(),
                                     ['^title', 'description'])

    # views.py
    from django.shortcuts import render
    from .forms import SearchForm

    @render('search.html')
    def search(request):
        form = SearchForm(request.GET or {})
        if form.is_valid():
            results = form.get_queryset()
        else:
            results = MyModel.objects.none()

        return {
            'form': form,
            'results': results,
        }


## Running tests

Use tox (<https://pypi.python.org/pypi/tox>):

    > pip install tox
    > cd path-to/django-simple-search
    > tox
