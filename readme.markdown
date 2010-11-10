See <http://gregbrown.co.nz/code/django-simple-search/> for details

Sample usage:

    class MyModelSearchForm(BaseSearchForm):
        class Meta:
            base_qs = MyModel.objects
            search_fields = ['^name','description', '@text', '=id'] 
    
    
        category = forms.ModelChoiceField(
            queryset = MyCategory.live.all()
        )
    