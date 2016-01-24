from __future__ import unicode_literals
import os
import sys

import django


def main():
    """
    This is the main test function called via ``python setup.py test``.
    """
    os.environ["DJANGO_SETTINGS_MODULE"] = "project.settings"
    django.setup()

    from django.core.management.commands import test
    sys.exit(test.Command().execute(verbosity=1))


if __name__ == "__main__":
    main()