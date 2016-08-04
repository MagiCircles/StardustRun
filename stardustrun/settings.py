# -*- coding: utf-8 -*-
from django.conf import settings as django_settings
from web.default_settings import DEFAULT_ENABLED_COLLECTIONS, DEFAULT_ENABLED_PAGES
from stardustrun import models, forms

SITE_NAME = 'Stardust Run'
SITE_URL = 'http://stardust.run/'
SITE_IMAGE = 'stardustrun.png'
SITE_STATIC_URL = '//localhost:{}/'.format(django_settings.DEBUG_PORT) if django_settings.DEBUG else '//i.stardust.run/'
GAME_NAME = u'Pokémon GO'
DISQUS_SHORTNAME = 'stardustrun'
ACCOUNT_MODEL = models.Account
COLOR = '#49d6b5'

ENABLED_COLLECTIONS = DEFAULT_ENABLED_COLLECTIONS

ENABLED_COLLECTIONS['account']['add']['form_class'] = forms.AccountForm
ENABLED_COLLECTIONS['account']['edit']['form_class'] = forms.AccountForm

ENABLED_PAGES = DEFAULT_ENABLED_PAGES
