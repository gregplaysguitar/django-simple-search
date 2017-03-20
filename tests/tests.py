from django.test import TestCase
from django.test import Client

from .models import MyCategory, MyModel

from simple_search import search_filter


def get_results(query_string, search_fields):
    return MyModel.objects.filter(search_filter(search_fields, query_string))


class SimpleSearchTestCase(TestCase):
    def setUp(self):
        # add some content
        first_category = MyCategory.objects.create(title='First category')
        second_category = MyCategory.objects.create(title='Second category')

        MyModel.objects.create(
            title='Line one', description='Beautiful is better than ugly.',
            category=first_category)
        MyModel.objects.create(
            title='Line two', description='Simple is better than complex.',
            category=first_category)
        MyModel.objects.create(
            title='Line three',
            description='Complex is better than complicated.',
            category=second_category)

    def test_search_filter(self):
        qs = get_results('simple', ['description'])
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0].title, 'Line two')

        qs = get_results('simple', ['title'])
        self.assertEqual(qs.count(), 0)

        qs = get_results('three', ['^title'])
        self.assertEqual(qs.count(), 0)

        qs = get_results('three', ['title'])
        self.assertEqual(qs.count(), 1)
        self.assertEqual(qs[0].title, 'Line three')

        qs = get_results('complex', ['description'])
        self.assertEqual(qs.count(), 2)

    def test_foreignkey(self):
        qs = get_results('first', ['category__title'])
        self.assertEqual(qs.count(), 2)
        self.assertEqual(qs[0].title, 'Line one')
        self.assertEqual(qs[1].title, 'Line two')

    def test_search_view(self):
        c = Client()

        response = c.get('/search?q=beautiful')
        self.assertEqual(response.content.decode("utf-8"), 'Line one')

        response = c.get('/search?q=complex')
        self.assertEqual(response.content.decode("utf-8"),
                         'Line two,Line three')

        response = c.get('/search?q=line')
        self.assertEqual(response.content.decode("utf-8"),
                         'Line one,Line two,Line three')
