from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
from anaf.core.rendering import JinjaRenderer, JinjaAjaxRenderer
__version__ = '0.1'

API_RENDERERS = (JSONRenderer, BrowsableAPIRenderer)
NOAPI_RENDERERS = (JinjaRenderer, JinjaAjaxRenderer)
