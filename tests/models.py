from django.db import models
from django.utils.encoding import python_2_unicode_compatible


@python_2_unicode_compatible
class MyCategory(models.Model):
    title = models.CharField(max_length=100)


@python_2_unicode_compatible
class MyModel(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    category = models.ForeignKey(MyCategory, on_delete=models.CASCADE)

    def __str__(self):
        return self.title
