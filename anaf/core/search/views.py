"""
Core Search module views
"""

from anaf.core.rendering import render_to_response
from django.template import RequestContext
from anaf.core.decorators import treeio_login_required, handle_response_format
from anaf.core.conf import settings
from anaf.core.models import Object, Tag
from anaf.core.search import dbsearch
from whoosh import index, qparser


@treeio_login_required
@handle_response_format
def search_query(request, response_format='html'):
    """Account view"""

    objects = []
    query = request.GET.get('q', '')
    if query:
        if query[:5] == 'tags:':
            tag_names = query[5:].strip().split(',')
            tags = Tag.objects.filter(name__in=tag_names)
            objects = Object.objects.filter(tags__in=tags)
        else:
            search_engine = getattr(settings, 'SEARCH_ENGINE', 'whoosh')
            if search_engine == 'whoosh':
                ix = index.open_dir(settings.WHOOSH_INDEX)
                # Whoosh doesn't understand '+' or '-' but we can replace
                # them with 'AND' and 'NOT'.
                squery = query.replace(
                    '+', ' AND ').replace('|', ' OR ').replace(' ', ' OR ')
                parser = qparser.MultifieldParser(
                    ["name", "url", "type", "content"], schema=ix.schema)
                qry = parser.parse(squery)
                try:
                    qry = parser.parse(squery)
                except:
                    # don't show the user weird errors only because we don't
                    # understand the query.
                    # parser.parse("") would return None
                    qry = None
                if qry:
                    searcher = ix.searcher()
                    try:
                        hits = searcher.search(qry, limit=100)
                    except:
                        hits = []

                    hit_ids = [hit['id'] for hit in hits]

                    objects = Object.objects.filter(pk__in=hit_ids)
            elif search_engine == 'db':
                objects = dbsearch.search(query)
            else:
                raise RuntimeError('Unknown Search engine: %s' % search_engine)

    return render_to_response('core/search/query_view',
                              {'query': query, 'objects': objects},
                              context_instance=RequestContext(request),
                              response_format=response_format)
