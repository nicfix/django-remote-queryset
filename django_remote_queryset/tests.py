import unittest

from django_remote_queryset.queries import QueryDecoder, Filter, CompositeQuery


class QueryTest(unittest.TestCase):

    def test_filter(self):
        json_query = \
            {
                '_query_class': 'compositequery',
                '_sub_queries': [{
                    '_query_class': 'filter',
                    '_condition': 'name__icontains',
                    '_value': 'nicola'
                }]
            }

        query = QueryDecoder.decodeJSONQuery(json_query)

        assert query

        assert isinstance(query, CompositeQuery)

        assert isinstance(query.get_sub_queries()[0], Filter)