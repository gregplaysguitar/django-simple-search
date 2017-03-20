from django.test import TestCase

from .models import MyModel

from simple_search import search_filter


def get_results(query_string, search_fields):
    return MyModel.objects.filter(search_filter(query_string, search_fields))


class SimpleSearchTestCase(TestCase):
    def setUp(self):
        # add some content
        MyModel.objects.create(
            title='Line one', description='Beautiful is better than ugly.')
        MyModel.objects.create(
            title='Line two', description='Simple is better than complex.')
        MyModel.objects.create(
            title='Line three',
            description='Complex is better than complicated.')

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
