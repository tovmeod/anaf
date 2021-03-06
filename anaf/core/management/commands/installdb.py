from distutils.util import strtobool
from django.core.management.base import BaseCommand, CommandError
from anaf.core.conf import settings
import json
import subprocess
import sys


class Command(BaseCommand):
    args = ''
    help = 'Installs the database prompting the user for all details'

    def handle(self, *args, **options):

        initial_db = {
            'ENGINE': 'django.db.backends.sqlite3',
            'NAME': './initial.db',
            'HOST': '',
            'USER': '',
            'PASSWORD': ''
        }

        db = {}

        dbengine = raw_input(
            'Enter database engine <mysql,postgresql,postgresql_psycopg2,oracle,sqlite3> (defaults to postgres): ')
        if not dbengine:
            dbengine = 'postgresql_psycopg2'
        if dbengine in ('mysql', 'postgresql', 'postgresql_psycopg2', 'oracle', 'sqlite3'):
            dbengine = 'django.db.backends.' + dbengine
        else:
            raise CommandError('Unknown database engine: {0!s}'.format(dbengine))

        if dbengine.endswith('sqlite3'):
            dbname = raw_input(
                'Enter database name (defaults to anaf.db): ')
            if not dbname:
                dbname = 'anaf.db'
        else:
            dbname = raw_input(
                'Enter database name (defaults to anaf): ')
            if not dbname:
                dbname = 'anaf'

            dbuser = raw_input('Database user (defaults to anaf): ')
            if not dbuser:
                dbuser = 'anaf'

            dbpassword = raw_input('Database password: ')

            dbhost = raw_input('Hostname (defaults to 127.0.0.1): ')
            if not dbhost:
                dbhost = '127.0.0.1'
            dbport = raw_input('Port (empty for default): ')

        self.stdout.write('\n-- Saving database configuration...\n')
        self.stdout.flush()
        settings.CONF.set('db', 'ENGINE', dbengine)
        settings.CONF.set('db', 'NAME', dbname)
        if not dbengine.endswith('sqlite3'):
            settings.CONF.set('db', 'USER', dbuser)
            settings.CONF.set('db', 'PASSWORD', dbpassword)
            settings.CONF.set('db', 'HOST', dbhost)
            settings.CONF.set('db', 'PORT', dbport)

        with open(settings.USER_CONFIG_FILE, 'w') as f:
            settings.CONF.write(f)

        answer = raw_input(
            'Would you like to create the tables (say no to use an existing database) [y/n] (defaults to yes): ')
        if not answer:
            answer = True
        else:
            answer = strtobool(answer)

        if answer:
            exit_code = subprocess.call(
                [sys.executable, 'manage.py', 'migrate'])
            if not exit_code == 0:
                self.stdout.flush()
                raise CommandError('Failed to install database.')

            self.stdout.write(
                '\n-- Successfully installed database. \n-- You\'re ready to go!\n\n')
