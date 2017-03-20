from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class MyModel(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()

    def __str__(self):
        return self.title
