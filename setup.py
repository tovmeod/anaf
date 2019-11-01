import os
from distutils.core import setup
from setuptools import find_packages
import anaf

setup(
        name='anaf',
        version=anaf.__version__,
        packages=find_packages(),
        include_package_data=True,
        package_data={'minidetector': ['search_strings.txt']},
        data_files=[('', ['anaf.ini'])],
        install_requires=[
            "Django<1.8",
            "whoosh",
            "django-websocket",
            "djangorestframework==3.9.1",
            "django-dajaxice==0.6",
            "django-dajax==0.9.2",
            "django-simple-captcha",
            "django-markup-deprecated",
            "django-pandora",
            "unidecode",
            "jinja2==2.5.2",
            "html5lib==0.90",
            "python-dateutil<2.0",
            "oauth2",
            "django-piston3==0.3rc2",
            "johnny-cache==1.6.1.a",
            "coffin==0.4.0",
        ],
        url='https://github.com/tovmeod/anaf',
        license='BSD',
        author='Avraham Seror',
        author_email='',
        description='A Business Management Platform',
        long_description=open(os.path.join(os.path.dirname(__file__), 'README.md')).read(),
        test_suite="project.runtests.main",
        tests_require=[
            "freezegun==0.3.5",
            # "pyflakes>=0.6.1",
            # "pep8>=1.4.1"
        ],
)
