#!/usr/bin/env python
# -*- coding: utf-8 -*-

__version__ = '1.0'
VERSION = tuple(map(int, __version__.split('.')))

import re
from django.db.models import Q
from django.db.models.query import QuerySet
from django import forms

from django.utils.text import smart_split
from django.conf import settings
from django.core.exceptions import FieldError



DEFAULT_STOPWORDS = 'a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your'


if hasattr(settings, 'DATABASES'):
    DATABASE_ENGINE =  settings.DATABASES[settings.DATABASES.keys()[0]]['ENGINE'].split('.')[-1]
else:
    DATABASE_ENGINE =  settings.DATABASE_ENGINE


    
class BaseSearchForm(forms.Form):
    STOPWORD_LIST = DEFAULT_STOPWORDS.split(',')
    DEFAULT_OPERATOR = Q.__and__
    
    q = forms.CharField(label='Search', required=False)
    def clean_q(self):
        return self.cleaned_data['q'].strip()
        
    order_by = forms.CharField(
        widget=forms.HiddenInput(),
        required=False,
    )
    
      
    class Meta:
        abstract = True
        base_qs = None
        
        # example: ['name', 'category__name', '@description', '=id']
        search_fields = None
        
        # should be a list of  pairs, of the form ('field1,field2', WEIGHTING)
        # where WEIGHTING is an integer. Assumes the relevant indexes have been
        # created
        fulltext_indexes = None
        
        
    def construct_search(self, field_name, first):
        if field_name.startswith('^'):
            if first:
                return "%s__istartswith" % field_name[1:]
            else:
                return "%s__icontains" % field_name[1:]
        elif field_name.startswith('='):
            return "%s__iexact" % field_name[1:]
        elif field_name.startswith('@'):
            if DATABASE_ENGINE == 'mysql':
                return "%s__search" % field_name[1:]
            else:
                return "%s__icontains" % field_name[1:]
        else:
            return "%s__icontains" % field_name
    
    
    def get_text_query_bits(self, query_string):
        """filter stopwords but only if there are useful words"""
        
        split_q = list(smart_split(query_string))
        filtered_q = []
        
        for bit in split_q:
            if bit not in self.STOPWORD_LIST:
                filtered_q.append(bit)
        
        if len(filtered_q):
            return filtered_q
        else:
            return split_q
    
    
    def get_text_search_query(self, query_string):
        filters = []
        first = True
            
        for bit in self.get_text_query_bits(query_string):
            or_queries = [Q(**{self.construct_search(str(field_name), first): bit}) for field_name in self.Meta.search_fields]
            filters.append(reduce(Q.__or__, or_queries))
            first = False
       
        if len(filters):
            return reduce(self.DEFAULT_OPERATOR, filters)
        else:
            return False
            

    def construct_filter_args(self, cleaned_data):
        args = []
                
        # if its an instance of Q, append to filter args
        # otherwise assume an exact match lookup
        for field in cleaned_data:
             
            if hasattr(self, 'prepare_%s' % field):
                q_obj = getattr(self, 'prepare_%s' % field)()
                if q_obj:
                    args.append(q_obj)
            elif isinstance(cleaned_data[field], Q):
                args.append(cleaned_data[field])
            elif field == 'order_by':
                pass # special case - ordering handled in get_result_queryset
            elif cleaned_data[field]:
                if isinstance(cleaned_data[field], list) or isinstance(cleaned_data[field], QuerySet):
                    args.append(Q(**{field + '__in': cleaned_data[field]}))
                else:
                    args.append(Q(**{field: cleaned_data[field]}))
        
        return args
    
        
    def get_result_queryset(self):
        qs = self.Meta.base_qs
        cleaned_data = self.cleaned_data.copy()
        query_text = cleaned_data.pop('q', None)
        
        qs = qs.filter(*self.construct_filter_args(cleaned_data))

        if query_text:
            fulltext_indexes = getattr(self.Meta, 'fulltext_indexes', None)
            if DATABASE_ENGINE == 'mysql' and fulltext_indexes:
                # cross-column fulltext search if db is mysql, otherwise use default behaviour.
                # We're assuming the appropriate fulltext index has been created
                match_bits = []
                params = []
                for index in fulltext_indexes:
                    match_bits.append('MATCH(%s) AGAINST (%%s) * %s' % index)
                    params.append(query_text)
                
                match_expr = ' + '.join(match_bits)
                
                qs = qs.extra(
                    select={'relevance': match_expr},
                    where=(match_expr,),
                    params=params,
                    select_params=params,
                    order_by=('-relevance',)
                )
                    
            else:
                # construct text search for sqlite, or for when no fulltext indexes are defined
                text_q = self.get_text_search_query(query_text)
                if text_q:
                    qs = qs.filter(text_q)
                else:
                    qs = qs.none()

        if self.cleaned_data['order_by']:
            qs = qs.order_by(*self.cleaned_data['order_by'].split(','))
                            
        return qs
    
