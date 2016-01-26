import json

from django.test import TestCase as DjangoTestCase


class TestCase(DjangoTestCase):
    """
    Base class for tests, common functionality will be here
    """
    def cmpDataApi(self, old, new, fieldname='root'):
        """
        Compares data using the old API with data retrieved with the new
        They don't need to be equivalent, the new API may return at least the data the old API was able to and may add
        :param str or dict or list old: content retrieved using the old API
        :param str or dict or list new: content retrieved using the new DRF API
        :return bool: is it kosher?
        """
        if isinstance(old, basestring):
            old = json.loads(old)
        if isinstance(new, basestring):
            new = json.loads(new)
        if isinstance(old, dict) and isinstance(new, dict):
            for k, v in sorted(old.items()):
                if k == 'resource_uri':
                        continue
                assert k in new, 'Field {}.{} not found on new.\nold:{}\nnew:{}'.format(fieldname, k, old, new)
                assert isinstance(v, type(new[k])),\
                    'Field {}.{} exists but have different content type.\nold:{}\nnew:{}'.format(fieldname, k, v, new[k])
                if isinstance(v, dict):
                    self.cmpDataApi(v, new[k], '{}.{}'.format(fieldname, k))
                elif isinstance(v, basestring):
                    assert v == new[k], 'Field {}.{} exists but have different value.\nold:{}\nnew:{}'.format(fieldname, k,
                                                                                                              v, new[k])
                else:
                    assert v == new[k]
        elif isinstance(old, list) and isinstance(new, list):
            old.sort(key=lambda x: x['id'])
            new.sort(key=lambda x: x['id'])
            for i, v in enumerate(old):
                self.cmpDataApi(v, new[i], str(i))
        else:
            assert False, 'old and new have different types'
