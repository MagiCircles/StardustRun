from django.conf import settings as django_settings
from web.default_settings import DEFAULT_ENABLED_COLLECTIONS, DEFAULT_ENABLED_PAGES
from stardustrun import models, forms

SITE_NAME = 'Sample Website'
SITE_URL = 'http://stardustrun.com/'
SITE_IMAGE = 'stardustrun.png'
SITE_STATIC_URL = '//localhost:{}/'.format(django_settings.DEBUG_PORT) if django_settings.DEBUG else '//i.stardustrun.com/'
GAME_NAME = 'Sample Game'
DISQUS_SHORTNAME = 'stardustrun'
ACCOUNT_MODEL = models.Account
COLOR = '#4a86e8'

ENABLED_COLLECTIONS = DEFAULT_ENABLED_COLLECTIONS

ENABLED_COLLECTIONS['account']['add']['form_class'] = forms.AccountForm
ENABLED_COLLECTIONS['account']['edit']['form_class'] = forms.AccountForm

ENABLED_PAGES = DEFAULT_ENABLED_PAGES
