"""
Compression middleware
"""
from django.utils.html import strip_spaces_between_tags as short
from treeio.core.conf import settings


def _minify_json(data):
    "Compress JSON"
    import json
    return json.dumps(json.loads(data))


class SpacelessMiddleware(object):

    "Spaceless Middleware"

    def process_response(self, request, response):
        "Process response"
        if 'text/html' in response['Content-Type']:
            response.content = short(response.content)
        if settings.ANAF_MINIFY_JSON and settings.ANAF_RESPONSE_FORMATS['json'] in response['Content-Type']:
            response.content = _minify_json(response.content)
        return response
