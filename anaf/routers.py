from __future__ import unicode_literals
from django.core.exceptions import ImproperlyConfigured
from rest_framework.routers import DefaultRouter, Route, flatten, replace_methodname, DynamicDetailRoute, DynamicListRoute


class BetterRouter(DefaultRouter):
    DetailWithPOST = Route(
            url=r'^{prefix}/{lookup}{trailing_slash}$',
            mapping={
                'get': 'retrieve',
                'post': 'detail_post',
                'put': 'update',
                'patch': 'partial_update',
                'delete': 'destroy'
            },
            name='{basename}-detail',
            initkwargs={'suffix': 'Instance'}
        )

    def get_routes(self, viewset):
        """
        This is a copy of SimpleRouter.get_routes with one difference, it may direct POST to the retrieve function
        """

        known_actions = flatten([route.mapping.values() for route in self.routes if isinstance(route, Route)])

        # Determine any `@detail_route` or `@list_route` decorated methods on the viewset
        detail_routes = []
        list_routes = []
        for methodname in dir(viewset):
            attr = getattr(viewset, methodname)
            httpmethods = getattr(attr, 'bind_to_methods', None)
            detail = getattr(attr, 'detail', True)
            if httpmethods:
                if methodname in known_actions:
                    raise ImproperlyConfigured('Cannot use @detail_route or @list_route '
                                               'decorators on method "%s" '
                                               'as it is an existing route' % methodname)
                httpmethods = [method.lower() for method in httpmethods]
                if detail:
                    detail_routes.append((httpmethods, methodname))
                else:
                    list_routes.append((httpmethods, methodname))

        def _get_dynamic_routes(route, dynamic_routes):
            ret = []
            for httpmethods, methodname in dynamic_routes:
                method_kwargs = getattr(viewset, methodname).kwargs
                initkwargs = route.initkwargs.copy()
                initkwargs.update(method_kwargs)
                url_path = initkwargs.pop("url_path", None) or methodname
                ret.append(Route(
                    url=replace_methodname(route.url, url_path),
                    mapping={httpmethod: methodname for httpmethod in httpmethods},
                    name=replace_methodname(route.name, url_path),
                    initkwargs=initkwargs,
                ))

            return ret

        ret = []
        for route in self.routes:
            if isinstance(route, DynamicDetailRoute):
                # Dynamic detail routes (@detail_route decorator)
                ret += _get_dynamic_routes(route, detail_routes)
            elif isinstance(route, DynamicListRoute):
                # Dynamic list routes (@list_route decorator)
                ret += _get_dynamic_routes(route, list_routes)
            elif route.url == r'^{prefix}/{lookup}{trailing_slash}$':
                # Detail route
                if hasattr(viewset, 'detail_post'):
                    ret.append(self.DetailWithPOST)
                else:
                    ret.append(route)
            else:
                # List route
                ret.append(route)

        return ret
