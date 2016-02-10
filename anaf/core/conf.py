# -*- coding: utf-8 -*-
"""
Multitenancy settings
"""

from django.conf import LazySettings
from pandora import box

DEFAULTS = {
    'MODULE_IDENTIFIER': 'hmodule',
    'RESPONSE_FORMATS': {
                'html': 'text/html',
                'mobile': 'text/html',
                'json': 'text/plain',
                # 'json': 'application/json',
                'ajax': 'text/plain',
                # 'ajax': 'application/json',
                'csv': 'text/csv',
                'xls': 'text/xls',
                'pdf': 'application/pdf',
                'rss': 'application/rss+xml',
    },
    'EMAIL_SERVER': '127.0.0.1',
    'IMAP_SERVER': '',
    'EMAIL_USERNAME': None,
    'EMAIL_PASSWORD': None,
    'EMAIL_FROM': 'noreply@anaf',
    'DEFAULT_SIGNATURE': """
Thanks!
The Anaf Team
            """,
    'DEFAULT_USER_ID': 1,
    'DEFAULT_PERMISSIONS': 'everyone',
    'SEND_EMAIL_TO_CALLER': True,
    'ALLOW_EMAIL_NOTIFICATIONS': True,
    'ALLOW_GRITTER_NOTIFICATIONS': True,
    'IMAGE_MAX_SIZE': (300, 400),
    'IMAGE_RESIZE_FILTER': 'ANTIALIAS',
    'MINIFY_JSON': False,
    'PAGINATOR_LENGTH': 20,
    'PAGINATOR_PAGES': 15,
    # How often should we loop through jobs, add/remove from pool, recycle jobs:
    'CRON_PERIOD': 60,
    # Number of cycles to keep HIGH priority jobs before forcefully terminating
    'CRON_HIGH_PRIORITY': 10,
    # Number of cycles to keep LOW priority jobs before forcefully terminating
    'CRON_LOW_PRIORITY': 3,
    # Number of seconds since last access to domain to give the job HIGH priority
    'CRON_QUALIFY_HIGH': 10,
    # Number of seconds since last access to domain to run cron jobs for the domain
    # 86400 seconds == 1 day
    'CRON_QUALIFY_RUN': 86400,
    # Number of jobs to keep in the pool at the same time
    'CRON_POOL_SIZE': 10,
    # Priority value at which we should try to gracefully end a job
    'CRON_SOFT_KILL': 0,
    # Priority value at which we must kill a job using any possible means (kill -9 job)
    'CRON_HARD_KILL': -1,
    # Seconds to wait between SIGKILL signals to a dead job
    'CRON_GRACE_WAIT': 5,
    'CRON_DISABLED': True,
    'MULTIPLE_LOGINS_DISABLED': False,
    'MESSAGING_POP3_LIMIT': 100,
    'MESSAGING_IMAP_LIMIT': 100,
    'MESSAGING_UNSAFE_BLOCKS': (
        'head', 'object', 'embed', 'applet', 'noframes', 'noscript', 'noembed', 'iframe', 'frame', 'frameset'
    ),
    'MESSAGING_IMAP_DEFAULT_FOLDER_NAME': 'UNSEEN',
    'SIGNALS_AUTOCREATE_USER': True,
    'HELP_LINK_PREFIX': '/help/',
    'HELP_SOURCE': 'http://www.anaf.website/help',
    'LANGUAGES': (
        ('en', u'English'),
        ('de', u'Deutsche'),
        ('el', u'ελληνικά'),
        ('es', u'Español'),
        ('fr', u'Français'),
        ('it', u'Italiano'),
        ('pt_BR', u'Português Brasileiro'),
        ('pt_PT', u'Português'),
        ('ru', u'Русский'),
        ('zh_CN', u'简体中文'),
    ),
    'LANGUAGES_DEFAULT': 'en',
    'AJAX_RELOAD_ON_REDIRECT': (
        'home',
        'user_login',
        'account_settings_view',
        'core_admin_index_perspectives',
        'core_admin_perspective_view',
        'core_settings_view'
    ),
    'FORCE_AJAX_RENDERING': True,
    # 49 is (GMT+00:00) UTC
    'SERVER_DEFAULT_TIMEZONE': 49,
    'SERVER_TIMEZONE': (
        ('0', u'(GMT-11:00) International Date Line West'),
        ('1', u'(GMT-11:00) Midway Island'), ('2', u'(GMT-11:00) Samoa'),
        ('3', u'(GMT-10:00) Hawaii'), ('4', u'(GMT-09:00) Alaska'),
        ('5', u'(GMT-08:00) Tijuana'), ('6', u'(GMT-08:00) Pacific Time (US & Canada)'),
        ('7', u'(GMT-07:00) Arizona'), ('8', u'(GMT-07:00) Arizona'),
        ('9', u'(GMT-08:00) Pacific Time (US & Canada)'), ('10', u'(GMT-07:00) Arizona'),
        ('11', u'(GMT-07:00) Mountain Time (US & Canada)'), ('12', u'(GMT-07:00) Chihuahua'),
        ('13', u'(GMT-07:00) Mazatlan'), ('14', u'(GMT-06:00) Central Time (US & Canada)'),
        ('15', u'(GMT-06:00) Guadalajara'), ('16', u'(GMT-06:00) Mexico City'),
        ('17', u'(GMT-06:00) Monterrey'), ('18', u'(GMT-06:00) Saskatchewan'),
        ('19', u'(GMT-05:00) Eastern Time (US & Canada)'), ('20', u'(GMT-05:00) Indiana (East)'),
        ('21', u'(GMT-05:00) Bogota'), ('22', u'(GMT-05:00) Lima'),
        ('23', u'(GMT-05:00) Quito'), ('24', u'(GMT-04:30) Caracas'),
        ('25', u'(GMT-04:00) Atlantic Time (Canada)'), ('26', u'(GMT-04:00) La Paz'),
        ('27', u'(GMT-04:00) Santiago'), ('28', u'(GMT-03:30) Newfoundland'),
        ('29', u'(GMT-08:00) Pacific Time (US & Canada)'), ('30', u'(GMT-03:00) Brasilia'),
        ('31', u'(GMT-03:00) Buenos Aires'), ('32', u'(GMT-03:00) Georgetown'),
        ('33', u'(GMT-03:00) Greenland'), ('34', u'(GMT-02:00) Mid-Atlantic'),
        ('35', u'(GMT-01:00) Azores'), ('36', u'(GMT-01:00) Cape Verde Is.'),
        ('37', u'(GMT+00:00) Casablanca'), ('38', u'(GMT+00:00) Dublin'),
        ('39', u'(GMT+00:00) Edinburgh'), ('40', u'(GMT+00:00) Lisbon'),
        ('41', u'(GMT+00:00) London'), ('42', u'(GMT+00:00) Monrovia'),
        ('43', u'(GMT+00:00) UTC'), ('44', u'(GMT+01:00) Amsterdam'),
        ('45', u'(GMT+01:00) Belgrade'), ('46', u'(GMT+01:00) Berlin'),
        ('47', u'(GMT+01:00) Bern'), ('48', u'(GMT+01:00) Bratislava'),
        ('49', u'(GMT+01:00) Brussels'), ('50', u'(GMT+01:00) Budapest'),
        ('51', u'(GMT+01:00) Copenhagen'), ('52', u'(GMT+01:00) Ljubljana'),
        ('53', u'(GMT+01:00) Madrid'), ('54', u'(GMT+01:00) Paris'),
        ('55', u'(GMT+01:00) Prague'), ('56', u'(GMT+01:00) Rome'),
        ('57', u'(GMT+01:00) Sarajevo'), ('58', u'(GMT+01:00) Skopje'),
        ('59', u'(GMT+01:00) Stockholm'), ('60', u'(GMT+01:00) Vienna'),
        ('61', u'(GMT+01:00) Warsaw'), ('62', u'(GMT+01:00) West Central Africa'),
        ('63', u'(GMT+01:00) Zagreb'), ('64', u'(GMT+02:00) Athens'),
        ('65', u'(GMT+02:00) Bucharest'), ('66', u'(GMT+02:00) Cairo'),
        ('67', u'(GMT+02:00) Harare'), ('68', u'(GMT+02:00) Helsinki'),
        ('69', u'(GMT+02:00) Istanbul'), ('70', u'(GMT+02:00) Jerusalem'),
        ('71', u'(GMT+02:00) Kyev'), ('72', u'(GMT+02:00) Minsk'),
        ('73', u'(GMT+02:00) Pretoria'), ('74', u'(GMT+02:00) Riga'),
        ('75', u'(GMT+02:00) Sofia'), ('76', u'(GMT+02:00) Tallinn'),
        ('77', u'(GMT+02:00) Vilnius'), ('78', u'(GMT+03:00) Baghdad'),
        ('79', u'(GMT+03:00) Kuwait'), ('80', u'(GMT+03:00) Moscow'),
        ('81', u'(GMT+03:00) Nairobi'), ('82', u'(GMT+03:00) Riyadh'),
        ('83', u'(GMT+03:00) St. Petersburg'), ('84', u'(GMT+03:00) Volgograd'),
        ('85', u'(GMT+03:30) Tehran'), ('86', u'(GMT+04:00) Abu Dhabi'),
        ('87', u'(GMT+04:00) Baku'), ('88', u'(GMT+04:00) Muscat'),
        ('89', u'(GMT+04:00) Tbilisi'), ('90', u'(GMT+04:00) Yerevan'),
        ('91', u'(GMT+04:30) Kabul'), ('92', u'(GMT+05:00) Ekaterinburg'),
        ('93', u'(GMT+05:00) Islamabad'), ('94', u'(GMT+05:00) Karachi'),
        ('95', u'(GMT+05:00) Tashkent'), ('96', u'(GMT+05:30) Chennai'),
        ('97', u'(GMT+05:30) Kolkata'), ('98', u'(GMT+05:30) Mumbai'),
        ('99', u'(GMT+05:30) New Delhi'), ('100', u'(GMT+05:30) Sri Jayawardenepura'),
        ('101', u'(GMT+05:45) Kathmandu'), ('102', u'(GMT+06:00) Almaty'),
        ('103', u'(GMT+06:00) Astana'), ('104', u'(GMT+06:00) Dhaka'),
        ('105', u'(GMT+06:00) Novosibirsk'), ('106', u'(GMT+06:30) Rangoon'),
        ('107', u'(GMT+07:00) Bangkok'), ('108', u'(GMT+07:00) Hanoi'),
        ('109', u'(GMT+07:00) Jakarta'), ('110', u'(GMT+07:00) Krasnoyarsk'),
        ('111', u'(GMT+08:00) Beijing'), ('112', u'(GMT+08:00) Chongqing'),
        ('113', u'(GMT+08:00) Hong Kong'), ('114', u'(GMT+08:00) Irkutsk'),
        ('115', u'(GMT+08:00) Kuala Lumpur'), ('116', u'(GMT+08:00) Perth'),
        ('117', u'(GMT+08:00) Singapore'), ('118', u'(GMT+08:00) Taipei'),
        ('119', u'(GMT+08:00) Ulaan Bataar'), ('120', u'(GMT+08:00) Urumqi'),
        ('121', u'(GMT+09:00) Osaka'), ('122', u'(GMT+09:00) Sapporo'),
        ('123', u'(GMT+09:00) Seoul'), ('124', u'(GMT+09:00) Tokyo'),
        ('125', u'(GMT+09:00) Yakutsk'), ('126', u'(GMT+09:30) Adelaide'),
        ('127', u'(GMT+09:30) Darwin'), ('128', u'(GMT+10:00) Brisbane'),
        ('129', u'(GMT+10:00) Canberra'), ('130', u'(GMT+10:00) Guam'),
        ('131', u'(GMT+10:00) Hobart'), ('132', u'(GMT+10:00) Melbourne'),
        ('133', u'(GMT+10:00) Port Moresby'), ('134', u'(GMT+10:00) Sydney'),
        ('135', u'(GMT+10:00) Vladivostok'), ('136', u'(GMT+11:00) Magadan'),
        ('137', u'(GMT+11:00) New Caledonia'), ('138', u'(GMT+11:00) Solomon Is.'),
        ('139', u'(GMT+12:00) Auckland'), ('140', u'(GMT+12:00) Fiji'),
        ('141', u'(GMT+12:00) Kamchatka'), ('142', u'(GMT+12:00) Marshall Is.'),
        ('143', u'(GMT+12:00) Wellington'), ('144', u'(GMT+13:00) Nukualofa'),
    ),
    'OBJECT_BLACKLIST': [
        'id', 'creator', 'object_name', 'object_type', 'trash', 'full_access', 'read_access', 'nuvius_resource',
        'object_ptr', 'comments', 'likes', 'dislikes', 'tags', 'links', 'subscribers', 'read_by'
    ],
    'UPDATE_BLACKLIST': [
        'likes', 'dislikes', 'tags', 'reference', 'total', 'links', 'subscribers', 'read_by', 'date_created',
        'last_updated'
    ],
    'TIMEZONE_BLACKLIST': ['date_created', 'last_updated', 'time_from', 'time_to'],
    'SUBSCRIPTION_CUSTOMIZATION': True,
    'SUBSCRIPTION_USER_LIMIT': 0,
    'SUBSCRIPTION_BLOCKED': False,
    'DEMO_MODE': False,
    'API_CONSUMER_DB': 'default',
    'API_AUTH_ENGINE': 'basic',
}


class Settings(LazySettings):

    def __getattr__(self, key):
        if key in box:
            return box[key]
        else:
            if key.startswith('ANAF_'):
                name = key[5:]  # removes prefix
                if name in DEFAULTS:
                    return getattr(super(Settings, self), key, DEFAULTS[name])
            return super(Settings, self).__getattr__(key)

settings = Settings()
