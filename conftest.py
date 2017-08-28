import pytest
import importlib


@pytest.fixture(scope='function', autouse=True)
# @pytest.mark.django_db(transaction=True)
def finance_initial_data(transactional_db ):
    # todo this is very ugly but it is a workaround because using serialized_rollback is very slow and
    #  would mean monkey patching pytest-django
    # see https://github.com/pytest-dev/pytest-django/issues/341
    # https://code.djangoproject.com/ticket/22487
    # https://code.djangoproject.com/ticket/23727
    from anaf.finance.models import Currency
    my_module = importlib.import_module('anaf.finance.migrations.0003_initial_data')
    my_module._add_data(Currency)


@pytest.fixture(scope='function', autouse=True)
def contact_initial_data(transactional_db ):
    from anaf.identities.models import ContactType
    my_module = importlib.import_module('anaf.identities.migrations.0002_initial_data')
    my_module._add_data(ContactType)
