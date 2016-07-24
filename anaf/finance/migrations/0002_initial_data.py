# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations


currencies = [
    {'symbol': 'Lek', 'code': 'ALL', 'name': 'Albania Lek'},
    {'symbol': '\xd8\x8b', 'code': 'AFN', 'name': 'Afghanistan Afghani'},
    {'symbol': '$', 'code': 'ARS', 'name': 'Argentina Peso'},
    {'symbol': '\xc6\x92', 'code': 'AWG', 'name': 'Aruba Guilder'},
    {'symbol': '$', 'code': 'AUD', 'name': 'Australia Dollar'},
    {'symbol': '\xe2\x82\xbc', 'code': 'AZN', 'name': 'Azerbaijan Manat'},
    {'symbol': '$', 'code': 'BSD', 'name': 'Bahamas Dollar'},
    {'symbol': '$', 'code': 'BBD', 'name': 'Barbados Dollar'},
    {'symbol': 'p.', 'code': 'BYR', 'name': 'Belarus Ruble'},
    {'symbol': 'BZ$', 'code': 'BZD', 'name': 'Belize Dollar'},
    {'symbol': '$', 'code': 'BMD', 'name': 'Bermuda Dollar'},
    {'symbol': '$b', 'code': 'BOB', 'name': 'Bolivia Boliviano'},
    {'symbol': 'KM', 'code': 'BAM', 'name': 'Bosnia n  HerzegovinaConvertible Marka'},
    {'symbol': 'P', 'code': 'BWP', 'name': 'Botswana Pula'},
    {'symbol': '\xd0\xbb\xd0\xb2', 'code': 'BGN', 'name': 'Bulgaria Lev'},
    {'symbol': 'R$', 'code': 'BRL', 'name': 'Brazil Real'},
    {'symbol': '$', 'code': 'BND', 'name': 'Brunei Darussalam Dollar'},
    {'symbol': '\xe1\x9f\x9b', 'code': 'KHR', 'name': 'Cambodia Riel'},
    {'symbol': '$', 'code': 'CAD', 'name': 'Canada Dollar'},
    {'symbol': '$', 'code': 'KYD', 'name': 'Cayman Dollar'},
    {'symbol': '$', 'code': 'CLP', 'name': 'Chile Peso'},
    {'symbol': '\xc2\xa5', 'code': 'CNY', 'name': 'China Yuan Renminbi'},
    {'symbol': '$', 'code': 'COP', 'name': 'Colombia Peso'},
    {'symbol': '\xe2\x82\xa1', 'code': 'CRC', 'name': 'Costa i aColon'},
    {'symbol': 'kn', 'code': 'HRK', 'name': 'Croatia Kuna'},
    {'symbol': '\xe2\x82\xb1', 'code': 'CUP', 'name': 'Cuba Peso'},
    {'symbol': 'K\xc4\x8d', 'code': 'CZK', 'name': 'Czech Republic Koruna'},
    {'symbol': 'kr', 'code': 'DKK', 'name': 'Denmark Krone'},
    {'symbol': 'RD$', 'code': 'DOP', 'name': 'Dominican Republic Peso'},
    {'symbol': '$', 'code': 'XCD', 'name': 'East Caribbean Dollar'},
    {'symbol': '\xc2\xa3', 'code': 'EGP', 'name': 'Egypt Pound'},
    {'symbol': '$', 'code': 'SVC', 'name': 'El Salvador Colon'},
    {'symbol': 'kr', 'code': 'EEK', 'name': 'Estonia Kroon'},
    {'symbol': '\xe2\x82\xac', 'code': 'EUR', 'name': 'Euro Member Euro'},
    {'symbol': '\xc2\xa3', 'code': 'FKP', 'name': 'Falkland Islands Pound'},
    {'symbol': '$', 'code': 'FJD', 'name': 'Fiji Dollar'},
    {'symbol': '\xe2\x82\xbe', 'code': 'GEL', 'name': 'Georgia Lari'},
    {'symbol': '\xc2\xa2', 'code': 'GHC', 'name': 'Ghana Cedis'},
    {'symbol': '\xc2\xa3', 'code': 'GIP', 'name': 'Gibraltar Pound'},
    {'symbol': 'Q', 'code': 'GTQ', 'name': 'Guatemala Quetzal'},
    {'symbol': '\xc2\xa3', 'code': 'GGP', 'name': 'Guernsey Pound'},
    {'symbol': '$', 'code': 'GYD', 'name': 'Guyana Dollar'},
    {'symbol': 'L', 'code': 'HNL', 'name': 'Honduras Lempira'},
    {'symbol': '$', 'code': 'HKD', 'name': 'Hong o gDollar'},
    {'symbol': 'Ft', 'code': 'HUF', 'name': 'Hungary Forint'},
    {'symbol': 'kr', 'code': 'ISK', 'name': 'Iceland Krona'},
    {'symbol': '\xe2\x82\xb9', 'code': 'INR', 'name': 'India Rupee'},
    {'symbol': 'Rp', 'code': 'IDR', 'name': 'Indonesia Rupiah'},
    {'symbol': '\xef\xb7\xbc', 'code': 'IRR', 'name': 'Iran Rial'},
    {'symbol': '\xc2\xa3', 'code': 'IMP', 'name': 'Isle f ManPound'},
    {'symbol': '\xe2\x82\xaa', 'code': 'ILS', 'name': 'Israel Shekel'},
    {'symbol': 'J$', 'code': 'JMD', 'name': 'Jamaica Dollar'},
    {'symbol': '\xc2\xa5', 'code': 'JPY', 'name': 'Japan Yen'},
    {'symbol': '\xc2\xa3', 'code': 'JEP', 'name': 'Jersey Pound'},
    {'symbol': '\xd0\xbb\xd0\xb2', 'code': 'KZT', 'name': 'Kazakhstan Tenge'},
    {'symbol': '\xe2\x82\xa9', 'code': 'KPW', 'name': 'North Korea Won'},
    {'symbol': '\xe2\x82\xa9', 'code': 'KRW', 'name': 'South Korea Won'},
    {'symbol': '\xd0\xbb\xd0\xb2', 'code': 'KGS', 'name': 'Kyrgyzstan Som'},
    {'symbol': '\xe2\x82\xad', 'code': 'LAK', 'name': 'Laos Kip'},
    {'symbol': 'Ls', 'code': 'LVL', 'name': 'Latvia Lat'},
    {'symbol': '\xc2\xa3', 'code': 'LBP', 'name': 'Lebanon Pound'},
    {'symbol': '$', 'code': 'LRD', 'name': 'Liberia Dollar'},
    {'symbol': 'Lt', 'code': 'LTL', 'name': 'Lithuania Litas'},
    {'symbol': '\xd0\xb4\xd0\xb5\xd0\xbd', 'code': 'MKD', 'name': 'Macedonia Denar'},
    {'symbol': 'RM', 'code': 'MYR', 'name': 'Malaysia Ringgit'},
    {'symbol': '\xe2\x82\xa8', 'code': 'MUR', 'name': 'Mauritius Rupee'},
    {'symbol': '$', 'code': 'MXN', 'name': 'Mexico Peso'},
    {'symbol': '\xe2\x82\xae', 'code': 'MNT', 'name': 'Mongolia Tughrik'},
    {'symbol': 'MT', 'code': 'MZN', 'name': 'Mozambique Metical'},
    {'symbol': '$', 'code': 'NAD', 'name': 'Namibia Dollar'},
    {'symbol': '\xe2\x82\xa8', 'code': 'NPR', 'name': 'Nepal Rupee'},
    {'symbol': '\xc6\x92', 'code': 'ANG', 'name': 'Netherlands Antilles Guilder'},
    {'symbol': '$', 'code': 'NZD', 'name': 'New Zealand Dollar'},
    {'symbol': 'C$', 'code': 'NIO', 'name': 'Nicaragua Cordoba'},
    {'symbol': '\xe2\x82\xa6', 'code': 'NGN', 'name': 'Nigeria Naira'},
    {'symbol': 'kr', 'code': 'NOK', 'name': 'Norway Krone'},
    {'symbol': '\xef\xb7\xbc', 'code': 'OMR', 'name': 'Oman Rial'},
    {'symbol': '\xe2\x82\xa8', 'code': 'PKR', 'name': 'Pakistan Rupee'},
    {'symbol': 'B/.', 'code': 'PAB', 'name': 'Panama Balboa'},
    {'symbol': 'Gs', 'code': 'PYG', 'name': 'Paraguay Guarani'},
    {'symbol': 'S/.', 'code': 'PEN', 'name': 'Peru Nuevo Sol'},
    {'symbol': '\xe2\x82\xb1', 'code': 'PHP', 'name': 'Philippines Peso'},
    {'symbol': 'z\xc5\x82', 'code': 'PLN', 'name': 'Poland Zloty'},
    {'symbol': '\xef\xb7\xbc', 'code': 'QAR', 'name': 'Qatar Riyal'},
    {'symbol': 'lei', 'code': 'RON', 'name': 'Romania New Leu'},
    {'symbol': '\xe2\x82\xbd', 'code': 'RUB', 'name': 'Russia Ruble'},
    {'symbol': '\xc2\xa3', 'code': 'SHP', 'name': 'Saint e enaPound'},
    {'symbol': '\xef\xb7\xbc', 'code': 'SAR', 'name': 'Saudi r biaRiyal'},
    {'symbol': '\xd0\x94\xd0\xb8\xd0\xbd.', 'code': 'RSD', 'name': 'Serbia Dinar'},
    {'symbol': '\xe2\x82\xa8', 'code': 'SCR', 'name': 'Seychelles Rupee'},
    {'symbol': '$', 'code': 'SGD', 'name': 'Singapore Dollar'},
    {'symbol': '$', 'code': 'SBD', 'name': 'Solomon Islands Dollar'},
    {'symbol': 'S', 'code': 'SOS', 'name': 'Somalia Shilling'},
    {'symbol': 'S', 'code': 'ZAR', 'name': 'South Africa Rand'},
    {'symbol': '\xe2\x82\xa8', 'code': 'LKR', 'name': 'Sri Lanka Rupee'},
    {'symbol': 'kr', 'code': 'SEK', 'name': 'Sweden Krona'},
    {'symbol': 'CHF', 'code': 'CHF', 'name': 'Switzerland Franc'},
    {'symbol': '$', 'code': 'SRD', 'name': 'Suriname Dollar'},
    {'symbol': '\xc2\xa3', 'code': 'SYP', 'name': 'Syria Pound'},
    {'symbol': 'NT$', 'code': 'TWD', 'name': 'Taiwan New Dollar'},
    {'symbol': '\xe0\xb8\xbf', 'code': 'THB', 'name': 'Thailand Baht'},
    {'symbol': 'TT$', 'code': 'TTD', 'name': 'Trinidad n  TobagoDollar'},
    {'symbol': '\xe2\x82\xba', 'code': 'TRL', 'name': 'Turkey Lira'},
    {'symbol': '$', 'code': 'TVD', 'name': 'Tuvalu Dollar'},
    {'symbol': '\xe2\x82\xb4', 'code': 'UAH', 'name': 'Ukraine Hryvna'},
    {'symbol': '\xc2\xa3', 'code': 'GBP', 'name': 'United Kingdom Pound'},
    {'symbol': '$', 'code': 'USD', 'name': 'United States Dollar'},
    {'symbol': '$U', 'code': 'UYU', 'name': 'Uruguay Peso'},
    {'symbol': '\xd0\xbb\xd0\xb2', 'code': 'UZS', 'name': 'Uzbekistan Som'},
    {'symbol': 'Bs', 'code': 'VEF', 'name': 'Venezuela Bolivar Fuerte'},
    {'symbol': '\xe2\x82\xab', 'code': 'VND', 'name': 'VietNam Dong'},
    {'symbol': '\xef\xb7\xbc', 'code': 'YER', 'name': 'Yemen Rial'},
    {'symbol': 'Z$', 'code': 'ZWD', 'name': 'Zimbabwe Dollar'}
]


def _add_data(Currency):
    for c in currencies:
        if c['code'] == 'USD':
            c['is_default'] = True
        Currency(**c).save()


def add_data(apps, schema_editor):
    Currency = apps.get_model('finance', 'Currency')
    _add_data(Currency)


class Migration(migrations.Migration):

    dependencies = [
        ('finance', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(add_data),
    ]
