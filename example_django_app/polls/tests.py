from autofixture import AutoFixture
from django.test import TestCase

# Create your tests here.
from django_remote_queryset.queries import QueryDecoder
from polls.models import Poll


class QueryTester(TestCase):
    def setUp(self):
        fixture = AutoFixture(Poll)
        polls = fixture.create(10)
        for poll in polls:
            poll.title = 'Nicola'
            poll.save()

    def test_drq_query_filtering(self):
        json_query = \
            {
                '_query_class': 'compositequery',
                '_sub_queries': [{
                    '_query_class': 'filter',
                    '_condition': 'title__icontains',
                    '_value': 'nicola'
                }]
            }

        query = QueryDecoder.decodeJSONQuery(json_query)

        qs = query.applyOnQuerySet(Poll.objects.all())

        assert qs.count() != 0

    def tearDown(self):
        Poll.objects.all().delete()
