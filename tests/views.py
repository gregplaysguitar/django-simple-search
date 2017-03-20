# -*- coding: utf-8 -*-

from django.http import HttpResponse

from .models import MyModel
from simple_search import search_form_factory


SearchForm = search_form_factory(MyModel.objects.all(),
                                 ['^title', 'description'])


def search(request):
    form = SearchForm(request.GET or {})
    if form.is_valid():
        results = form.get_queryset()
    else:
        results = MyModel.objects.none()

    return HttpResponse(','.join(results.values_list('title', flat=True)))
