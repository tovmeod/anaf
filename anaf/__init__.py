import sys
from rest_framework.renderers import JSONRenderer, BrowsableAPIRenderer
__version__ = '0.1'

if sys.version_info > (3,):
    long_type = int
else:
    long_type = long

API_RENDERERS = (JSONRenderer, BrowsableAPIRenderer)