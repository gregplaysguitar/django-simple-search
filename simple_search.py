# -*- coding: utf-8 -*-

from django.db.models import Q
from django import forms
from django.utils.text import smart_split
from django.conf import settings


if not locals().get('reduce'):
    from functools import reduce


__version__ = '1.0.2'
VERSION = tuple(map(int, __version__.split('.')))


STOPWORDS = getattr(
    settings,
    'SEARCH_STOPWORDS',
    'a,able,about,across,after,all,almost,also,am,among,an,'
    'and,any,are,as,at,be,because,been,but,by,can,cannot,'
    'could,dear,did,do,does,either,else,ever,every,for,from,'
    'get,got,had,has,have,he,her,hers,him,his,how,however,i,'
    'if,in,into,is,it,its,just,least,let,like,likely,may,me,'
    'might,most,must,my,neither,no,nor,not,of,off,often,on,'
    'only,or,other,our,own,rather,said,say,says,she,should,'
    'since,so,some,than,that,the,their,them,then,there,'
    'these,they,this,tis,to,too,twas,us,wants,was,we,were,'
    'what,when,where,which,while,who,whom,why,will,with,'
    'would,yet,you,your').split(',')


NULL_FILTER = Q(pk=None)


def search_filter(search_fields, query_string):
    """search_fields example: ['name', 'category__name', '@description', '=id']
    """

    query_string = query_string.strip()

    filters = []
    first = True

    for bit in split_text_query(query_string):
        queries = [Q(**{search_param(field_name, first): bit})
                   for field_name in search_fields]
        filters.append(reduce(Q.__or__, queries))
        first = False

    return reduce(Q.__and__, filters) if len(filters) else NULL_FILTER


def search_param(field_name, is_first_word):
    if field_name.startswith('^') and is_first_word:
        return "%s__istartswith" % field_name[1:]
    elif field_name.startswith('@'):
        return "%s__search" % field_name[1:]
    elif field_name.startswith('='):
        return "%s__iexact" % field_name[1:]
    else:
        return "%s__icontains" % field_name


def split_text_query(query):
    """Filter out stopwords but only if there are useful words"""

    split_query = list(smart_split(query))
    filtered_query = [bit for bit in split_query if bit not in STOPWORDS]

    return filtered_query if len(filtered_query) else split_query


class SearchForm(forms.Form):
    queryset = None
    search_fields = None

    q = forms.CharField(label='Search', required=False)

    def clean_q(self):
        return self.cleaned_data['q'].strip()

    def get_queryset(self):
        qs = self.queryset
        query = self.cleaned_data.get('q')

        if query:
            qs = qs.filter(search_filter(self.search_fields, query))

        return qs


def search_form_factory(queryset, search_fields):
    _queryset = queryset
    _search_fields = search_fields

    class _Form(SearchForm):
        queryset = _queryset
        search_fields = _search_fields

    return _Form
