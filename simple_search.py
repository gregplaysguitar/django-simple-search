import re
from django.db.models import Q
from django.db.models.query import QuerySet
from django import forms

from django.utils.text import smart_split
from django.conf import settings
from django.core.exceptions import FieldError



DEFAULT_STOPWORDS = 'a,able,about,across,after,all,almost,also,am,among,an,and,any,are,as,at,be,because,been,but,by,can,cannot,could,dear,did,do,does,either,else,ever,every,for,from,get,got,had,has,have,he,her,hers,him,his,how,however,i,if,in,into,is,it,its,just,least,let,like,likely,may,me,might,most,must,my,neither,no,nor,not,of,off,often,on,only,or,other,our,own,rather,said,say,says,she,should,since,so,some,than,that,the,their,them,then,there,these,they,this,tis,to,too,twas,us,wants,was,we,were,what,when,where,which,while,who,whom,why,will,with,would,yet,you,your'

    
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
        search_fields = None
        
        
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
        split_q = list(smart_split(query_string))
        
        # filter stopwords but only if there are useful words
        filtered_q = []
        for bit in split_q:
            if bit not in self.STOPWORD_LIST:
                filtered_q.append(bit)
        for bit in (filtered_q if len(filtered_q) else split_q):
            or_queries = [Q(**{construct_search(str(field_name), first): bit}) for field_name in self.Meta.search_fields]
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
        
        
        # construct text search
        if cleaned_data['q']:
            text_q = self.get_text_search_query(cleaned_data.pop('q'))
            if text_q:
                qs = qs.filter(text_q)
            else:
                qs = qs.none()
        
        qs = qs.filter(*self.construct_filter_args(cleaned_data))


        if self.cleaned_data['order_by']:
            qs = qs.order_by(*self.cleaned_data['order_by'].split(','))
                            
        return qs