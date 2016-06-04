import sys
__version__ = '0.1a'

if sys.version_info > (3,):
    long_type = int
else:
    long_type = long
