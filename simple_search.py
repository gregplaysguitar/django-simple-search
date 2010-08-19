"""

See http://gregbrown.co.nz/code/django-simple-search/ for details

Sample usage:

    class MyModelSearchForm(BaseSearchForm):
        class Meta:
            base_qs = MyModel.objects
            search_fields = ['^name','description', '@text', '=id'] 
    
    
        category = forms.ModelChoiceField(
            queryset = MyCategory.live.all()
        )
    
    
"""


import re
from django.db.models import Q
from django import forms

from django.utils.text import smart_split
from django.conf import settings
from django.core.exceptions import FieldError


    
class BaseSearchForm(forms.Form):
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
        search_fields = None
        default_operator = Q.__and__

    def get_text_search_query(self, query_string):
        filters = []
        
        def construct_search(field_name, first):
            if field_name.startswith('^'):
                if first:
                    return "%s__istartswith" % field_name[1:]
                else:
                    return "%s__icontains" % field_name[1:]
            elif field_name.startswith('='):
                return "%s__iexact" % field_name[1:]
            elif field_name.startswith('@'):
                if settings.DATABASE_ENGINE == 'mysql':
                    return "%s__search" % field_name[1:]
                else:
                    return "%s__icontains" % field_name[1:]
            else:
                return "%s__icontains" % field_name
        
        first = True
        for bit in smart_split(query_string):
            or_queries = [Q(**{construct_search(str(field_name), first): bit}) for field_name in self.Meta.search_fields]
            filters.append(reduce(Q.__or__, or_queries))
            first = False
        
        return reduce(getattr(self.Meta, 'default_operator', Q.__and__), filters)


    def construct_filter_args(self, cleaned_data=None):
        args = []
        
        if not cleaned_data:
            cleaned_data = self.cleaned_data.copy()
        
        # construct text search
        if cleaned_data['q']:
            args.append(self.get_text_search_query(cleaned_data.pop('q')))
        
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
                args.append(Q(**{field: cleaned_data[field]}))
        
        return args
    
        
    def get_result_queryset(self):
        qs = self.Meta.base_qs.filter(*self.construct_filter_args())
        """
        for field_name in self.Meta.search_fields:
            if '__' in field_name:
                qs = qs.distinct()
                break
        """
        if self.cleaned_data['order_by']:
            qs = qs.order_by(*self.cleaned_data['order_by'].split(','))
                            
        return qs