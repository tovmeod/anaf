"""
Finance module URLs
"""
from django.conf.urls import patterns, url

from anaf.finance import views

urlpatterns = patterns('anaf.finance.views',
                       url(r'^(\.(?P<response_format>\w+))?$', views.index_transactions, name='finance'),

                       url(r'^index(\.(?P<response_format>\w+))?$', views.index_transactions,
                           name='finance_index_transactions'),
                       url(r'^categories(\.(?P<response_format>\w+))?/?$', views.index_categories,
                           name='finance_categories'),
                       url(r'^income(\.(?P<response_format>\w+))?/?$', views.income_view, name='finance_income_view'),
                       url(r'^balance(\.(?P<response_format>\w+))?/?$', views.balance_sheet,
                           name='finance_balance_sheet'),

                       # Accounts
                       url(r'^accounts(\.(?P<response_format>\w+))?/?$', views.index_accounts,
                           name='finance_index_accounts'),
                       url(r'^account/add(\.(?P<response_format>\w+))?/?$', views.account_add,
                           name='finance_account_add'),
                       url(r'^account/edit/(?P<account_id>\d+)(\.(?P<response_format>\w+))?/?$', views.account_edit,
                           name='finance_account_edit'),
                       url(r'^account/view/(?P<account_id>\d+)(\.(?P<response_format>\w+))?/?$', views.account_view,
                           name='finance_account_view'),
                       url(r'^account/delete/(?P<account_id>\d+)(\.(?P<response_format>\w+))?/?$', views.account_delete,
                           name='finance_account_delete'),

                       # Assets
                       url(r'^assets(\.(?P<response_format>\w+))?/?$', views.index_assets, name='finance_index_assets'),
                       url(r'^asset/add(\.(?P<response_format>\w+))?/?$', views.asset_add, name='finance_asset_add'),
                       url(r'^asset/edit/(?P<asset_id>\d+)(\.(?P<response_format>\w+))?/?$', views.asset_edit,
                           name='finance_asset_edit'),
                       url(r'^asset/view/(?P<asset_id>\d+)(\.(?P<response_format>\w+))?/?$', views.asset_view,
                           name='finance_asset_view'),
                       url(r'^asset/delete/(?P<asset_id>\d+)(\.(?P<response_format>\w+))?/?$', views.asset_delete,
                           name='finance_asset_delete'),

                       # Equities
                       url(r'^equities(\.(?P<response_format>\w+))?/?$', views.index_equities,
                           name='finance_index_equities'),
                       url(r'^equity/add(\.(?P<response_format>\w+))?/?$', views.equity_add, name='finance_equity_add'),
                       url(r'^equity/edit/(?P<equity_id>\d+)(\.(?P<response_format>\w+))?/?$', views.equity_edit,
                           name='finance_equity_edit'),
                       url(r'^equity/view/(?P<equity_id>\d+)(\.(?P<response_format>\w+))?/?$', views.equity_view,
                           name='finance_equity_view'),
                       url(r'^equity/delete/(?P<equity_id>\d+)(\.(?P<response_format>\w+))?/?$', views.equity_delete,
                           name='finance_equity_delete'),

                       # Transactions
                       url(r'^transactions(\.(?P<response_format>\w+))?/?$', views.index_transactions,
                           name='finance_index_transactions'),
                       url(r'^transaction/add/order/(?P<order_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.transaction_add, name='finance_transaction_add_order'),
                       url(r'^transaction/add/(?P<liability_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.transaction_add, name='finance_transaction_add'),
                       url(r'^transaction/add(\.(?P<response_format>\w+))?/?$', views.transaction_add,
                           name='finance_transaction_add'),
                       url(r'^transaction/edit/(?P<transaction_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.transaction_edit, name='finance_transaction_edit'),
                       url(r'^transaction/view/(?P<transaction_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.transaction_view, name='finance_transaction_view'),
                       url(r'^transaction/delete/(?P<transaction_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.transaction_delete, name='finance_transaction_delete'),

                       # Liabilities
                       url(r'^liabilities(\.(?P<response_format>\w+))?/?$', views.index_liabilities,
                           name='finance_index_liabilities'),
                       url(r'^liability/add(\.(?P<response_format>\w+))?/?$', views.liability_add,
                           name='finance_liability_add'),
                       url(r'^liability/edit/(?P<liability_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.liability_edit, name='finance_liability_edit'),
                       url(r'^liability/view/(?P<liability_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.liability_view, name='finance_liability_view'),
                       url(r'^liability/delete/(?P<liability_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.liability_delete, name='finance_liability_delete'),

                       # Receivables
                       url(r'^receivables(\.(?P<response_format>\w+))?/?$', views.index_receivables,
                           name='finance_index_receivables'),
                       url(r'^receivable/add(\.(?P<response_format>\w+))?/?$', views.receivable_add,
                           name='finance_receivable_add'),
                       url(r'^receivable/edit/(?P<receivable_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.receivable_edit, name='finance_receivable_edit'),
                       url(r'^receivable/view/(?P<receivable_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.receivable_view, name='finance_receivable_view'),
                       url(r'^receivable/delete/(?P<receivable_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.receivable_delete, name='finance_receivable_delete'),

                       # Categories
                       url(r'^category/add(\.(?P<response_format>\w+))?/?$', views.category_add,
                           name='finance_category_add'),
                       url(r'^category/edit/(?P<category_id>\d+)(\.(?P<response_format>\w+))?/?$', views.category_edit,
                           name='finance_category_edit'),
                       url(r'^category/view/(?P<category_id>\d+)(\.(?P<response_format>\w+))?/?$', views.category_view,
                           name='finance_category_view'),
                       url(r'^category/delete/(?P<category_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.category_delete, name='finance_category_delete'),

                       # Currencies
                       url(r'^currency/add(\.(?P<response_format>\w+))?/?$', views.currency_add,
                           name='finance_currency_add'),
                       url(r'^currency/edit/(?P<currency_id>\d+)(\.(?P<response_format>\w+))?/?$', views.currency_edit,
                           name='finance_currency_edit'),
                       url(r'^currency/view/(?P<currency_id>\d+)(\.(?P<response_format>\w+))?/?$', views.currency_view,
                           name='finance_currency_view'),
                       url(r'^currency/delete/(?P<currency_id>\d+)(\.(?P<response_format>\w+))?/?$',
                           views.currency_delete, name='finance_currency_delete'),

                       # Taxes
                       url(r'^tax/add(\.(?P<response_format>\w+))?/?$', views.tax_add, name='finance_tax_add'),
                       url(r'^tax/edit/(?P<tax_id>\d+)(\.(?P<response_format>\w+))?/?$', views.tax_edit,
                           name='finance_tax_edit'),
                       url(r'^tax/view/(?P<tax_id>\d+)(\.(?P<response_format>\w+))?/?$', views.tax_view,
                           name='finance_tax_view'),
                       url(r'^tax/delete/(?P<tax_id>\d+)(\.(?P<response_format>\w+))?/?$', views.tax_delete,
                           name='finance_tax_delete'),

                       # Settings
                       url(r'^settings/view(\.(?P<response_format>\w+))?/?$', views.settings_view,
                           name='finance_settings_view'),
                       url(r'^settings/edit(\.(?P<response_format>\w+))?/?$', views.settings_edit,
                           name='finance_settings_edit'),
                       )
