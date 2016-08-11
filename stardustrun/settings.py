# -*- coding: utf-8 -*-
from django.conf import settings as django_settings
from django.utils.translation import ugettext_lazy as _
from web.utils import tourldash
from web.default_settings import DEFAULT_ENABLED_COLLECTIONS, DEFAULT_ENABLED_PAGES, DEFAULT_JAVASCRIPT_TRANSLATED_TERMS
from stardustrun import models, forms, filters, utils, collections_settings as collections

SITE_NAME = 'Stardust Run'
SITE_URL = 'http://stardust.run/'
SITE_IMAGE = 'stardustrun.png'
SITE_STATIC_URL = '//localhost:{}/'.format(django_settings.DEBUG_PORT) if django_settings.DEBUG else '//i.stardust.run/'
GAME_NAME = u'Pokémon GO'
DISQUS_SHORTNAME = 'stardustrun'
ACCOUNT_MODEL = models.Account
COLOR = '#49d6b5'

SITE_DESCRIPTION = _(u'The Pokémon GO Sharing Community')

SHOW_TOTAL_ACCOUNTS = False

GITHUB_REPOSITORY = ('SchoolIdolTomodachi', 'StardustRun')
TWITTER_HANDLE = 'stardust_run'
HASHTAGS = ['PokemonGO']

SITE_LOGO = 'stardustrun_logo.png'

CALL_TO_ACTION = _(u'Share your Pokémons!')

GAME_DESCRIPTION = _(u'Pokémon Go is a free-to-play, location-based augmented reality game developed and published by Niantic for iOS and Android devices.')

TOTAL_DONATORS = getattr(django_settings, 'TOTAL_DONATORS', 2)

FAVORITE_CHARACTERS = getattr(django_settings, 'ALL_POKEMONS', None)
FAVORITE_CHARACTER_TO_URL = lambda link: '/pokemon/{pk}/{name}/'.format(pk=link.raw_value, name=tourldash(link.value))
FAVORITE_CHARACTER_NAME = _(u'{nth} Favorite Pokémon')

GET_GLOBAL_CONTEXT = utils.globalContext

DONATORS_STATUS_CHOICES = models.DONATORS_STATUS_CHOICES

JAVASCRIPT_TRANSLATED_TERMS = DEFAULT_JAVASCRIPT_TRANSLATED_TERMS
JAVASCRIPT_TRANSLATED_TERMS += [
    'Permalink',
    'Deleted',
]

EMPTY_IMAGE = 'pokeball_empty.png'

ON_USER_EDITED = utils.onUserEdited
ON_PREFERENCES_EDITED = utils.onPreferencesEdited

ENABLED_COLLECTIONS = DEFAULT_ENABLED_COLLECTIONS

ENABLED_COLLECTIONS['account']['list']['default_ordering'] = '-level'
ENABLED_COLLECTIONS['account']['list']['filter_form'] = forms.FilterAccounts
ENABLED_COLLECTIONS['account']['list']['filter_queryset'] = filters.filterAccounts
ENABLED_COLLECTIONS['account']['list']['js_files'] = ENABLED_COLLECTIONS['account']['list'].get('js_files', []) + ['leaderboard']
ENABLED_COLLECTIONS['account']['list']['extra_context'] = collections.leaderboardExtraContext
ENABLED_COLLECTIONS['account']['list']['before_template'] = 'include/accountsBeforeTemplate'

ENABLED_COLLECTIONS['account']['add']['redirect_after_add'] = collections.redirectAfterAddAccount

ENABLED_COLLECTIONS['account']['add']['form_class'] = collections.modAccountGetForm
ENABLED_COLLECTIONS['account']['edit']['form_class'] = forms.AdvancedAccountForm
ENABLED_COLLECTIONS['account']['add']['otherbuttons_template'] = 'include/accountAdvancedButton'

ENABLED_COLLECTIONS['account']['add']['extra_context'] = collections.modAccountExtraContext
ENABLED_COLLECTIONS['account']['edit']['extra_context'] = collections.modAccountExtraContext
ENABLED_COLLECTIONS['account']['add']['after_template'] = 'include/accountJSstarter'
ENABLED_COLLECTIONS['account']['edit']['after_template'] = 'include/accountJSstarter'
ENABLED_COLLECTIONS['account']['add']['js_files'] = ENABLED_COLLECTIONS['account']['add'].get('js_files', []) + ['accountsForm']
ENABLED_COLLECTIONS['account']['edit']['js_files'] = ENABLED_COLLECTIONS['account']['edit'].get('js_files', []) + ['accountsForm']

ENABLED_COLLECTIONS['account']['item'] = {
}

ENABLED_COLLECTIONS['user']['item']['js_files'] = ENABLED_COLLECTIONS['user']['item'].get('js_files', []) + ['profile_account_tabs']
ENABLED_COLLECTIONS['user']['item']['extra_context'] = collections.profileGetAccountTabs

ENABLED_COLLECTIONS['pokemon'] = {
    'queryset': models.Pokemon.objects.all(),
    'title': _(u'Pokémon'),
    'plural_title': _(u'Pokémons'),
    'icon': 'album',
    'list': {
        'filter_queryset': filters.filterPokemons,
        'default_ordering': 'id',
        'filter_form': forms.FilterPokemonsForm,
        'per_line': 4,
        'page_size': 16,
        'col_break': 'lg',
        'js_files': ['pokemons'],
        'ajax_pagination_callback': 'updatePokemons',
        'before_template': 'include/pokemonsBeforeTemplate',
        'extra_context': collections.pokemonsExtraContext,
        'after_template': 'include/pokemonsShareButton',
    },
    'item': {
        'template': 'pokemonFullItem',
        'extra_context': collections.pokemonFullItemContext,
        'ajax': True,
        'js_files': ['full_pokemon']
    },
    'add': {
        'form_class': forms.PokemonForm,
        'authentication_required': True,
        'staff_required': True,
        'multipart': True,
    },
    'edit': {
        'form_class': forms.PokemonForm,
        'staff_required': True,
        'allow_delete': True,
        'multipart': True,
    },
}

ENABLED_COLLECTIONS['attack'] = {
    'queryset': models.Attack.objects.all(),
    'title': _(u'Attack'),
    'plural_title': _(u'Attacks'),
    'navbar_link': False,
    'icon': 'index',
    'list': {
        'default_ordering': 'damage',
        'show_title': True,
        'per_line': 1,
        'filter_form': forms.FilterAttacksForm,
        'filter_queryset': filters.filterAttacks,
        'extra_context': collections.attacksExtraContext,
        'before_template': 'include/attacksBeforeTemplate',
        'js_files': ['attacks'],
    },
    'add': {
        'form_class': forms.AttackForm,
        'authentication_required': True,
        'staff_required': True,
        'redirect_after_add': '/attacks/'
    },
    'edit': {
        'form_class': forms.AttackForm,
        'staff_required': True,
        'allow_delete': True,
    },
}

ENABLED_COLLECTIONS['ownedpokemon'] = {
    'queryset': models.OwnedPokemon.objects.all(),
    'title': _(u'Pokémon'),
    'plural_title': _(u'Pokémons'),
    'navbar_link': False,
    'list': {
        'default_ordering': '-cp',
        'foreach_items': collections.foreachOwnedPokemon,
        'page_size': 48,
        'per_line': 4,
        'col_break': 'sm',
        'filter_queryset': filters.filterOwnedPokemons,
        'extra_context': collections.ownedPokemonsExtraContext,
        'ajax_pagination_callback': 'loadToolTips',
    },
    'edit': {
        'form_class': forms.EditOwnedPokemonForm,
        'allow_delete': True,
        'redirect_after_edit': collections.ownedPokemonRedirectAfter,
        'redirect_after_delete': collections.ownedPokemonRedirectAfter,
        'back_to_list_button': False,
        'js_files': ['edit_ownedpokemon'],
    },
}

ENABLED_PAGES = DEFAULT_ENABLED_PAGES

ENABLED_PAGES['pokedex'] = {
    'ajax': True,
    'navbar_link': False,
    'url_variables': {
        ('account', '\d+'),
    },
}

ENABLED_PAGES['add_pokemon'] = {
    'ajax': True,
    'navbar_link': False,
    'url_variables': [
        ('pokemon', '\d+'),
    ],
}

ENABLED_PAGES['change_candies'] = {
    'ajax': True,
    'navbar_link': False,
    'url_variables': [
        ('pokemon', '\d+'),
        ('account', '\d+'),
    ],
}

ENABLED_PAGES['change_seen'] = {
    'ajax': True,
    'navbar_link': False,
    'url_variables': [
        ('pokemon', '\d+'),
        ('account', '\d+'),
    ],
}

ENABLED_PAGES['change_caught'] = {
    'ajax': True,
    'navbar_link': False,
    'url_variables': [
        ('pokemon', '\d+'),
        ('account', '\d+'),
    ],
}

ENABLED_PAGES['level_up'] = {
    'ajax': True,
    'navbar_link': False,
    'url_variables': [
        ('account', '\d+'),
    ],
}

ENABLED_PAGES['evolve'] = [
    {
        'title': _('Evolve'),
        'navbar_link': False,
        'url_variables': [
            ('ownedpokemon', '\d+'),
        ],
    },
    {
        'title': _('Evolve'),
        'ajax': True,
        'navbar_link': False,
        'url_variables': [
            ('ownedpokemon', '\d+'),
        ],
    },
]
