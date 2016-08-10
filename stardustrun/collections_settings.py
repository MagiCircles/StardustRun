# -*- coding: utf-8 -*-
from __future__ import division
from collections import OrderedDict
from django.db.models import Prefetch
from django.conf import settings as django_settings
from django.utils.translation import ugettext_lazy as _
from stardustrun import models, forms

############################################################
# Users

_profile_tabs = [
    ('Pokemons', _(u'Pokémons')),
    ('Pokedex', _(u'Pokédex')),
    ('Medals', _('Medals')),
]
_profile_tabs_dict = dict(_profile_tabs)

def profileGetAccountTabs(context):
    from web.views import profileExtraContext
    profileExtraContext(context)
    request = context['request']
    for account in context['item'].all_accounts:
        show = request.GET.get('account{}'.format(account.id), 'Pokemons')
        account.show = show if show in _profile_tabs_dict else 'Pokemons'
    context['account_tabs'] = _profile_tabs

############################################################
# Accounts

def redirectAfterAddAccount(request, item, ajax=False):
    if item.starter:
        models.Pokedex.objects.create(pokemon_id=item.starter_id, account=item, seen=True, caught=True)
        models.OwnedPokemon.objects.create(account=item, pokemon_id=item.starter_id)
    return '/pokemons/?get_started'

def modAccountExtraContext(context):
    context['starters_images'] = django_settings.STARTERS_IMAGES

def leaderboardExtraContext(context):
    request = context['request']
    context['starters_images'] = django_settings.STARTERS_IMAGES
    context['teams'] = [('', _('Global'), 'None')] + models.TEAM_CHOICES
    context['current_team'] = request.GET.get('team', '')

def modAccountGetForm(request, context, collection):
    formClass = forms.AccountForm
    if 'advanced' in request.GET:
        formClass = forms.AdvancedAccountForm
        context['advanced'] = True
    return formClass

############################################################
# Pokemons

def pokemonsExtraContext(context):
    request = context['request']
    if 'get_started' in request.GET:
        context['get_started'] = True
    if context['is_last_page']:
        context['share_sentence'] = _(u'Check out my awesome collection of Pokémons!')
    if 'ordering' in request.GET:
        context['ordering'] = request.GET['ordering']
    if 'type' in request.GET and request.GET['type']:
        context['type'] = request.GET['type']
    context['pokemon_types'] = models.POKEMON_TYPES_DICT

_full_pokemon_tabs = ['collection', 'evolutions', 'attacks']

def pokemonFullItemContext(context):
    request = context['request']
    context['stats'] = [
        OrderedDict([
            ('hit_points', {
                'value': context['item'].hit_points,
                'name': _('Hit Points'),
                'percent': (context['item'].hit_points / django_settings.POKEMONS_MAX_STATS['hit_points']) * 100,
            }),
            ('attack', {
                'value': context['item'].attack,
                'name': _('Attack'),
                'percent': (context['item'].attack / django_settings.POKEMONS_MAX_STATS['attack']) * 100,
            }),
            ('defense', {
                'value': context['item'].defense,
                'name': _('Defense'),
                'percent': (context['item'].defense / django_settings.POKEMONS_MAX_STATS['defense']) * 100,
            }),
        ]),
        OrderedDict([
            ('max_cp', {
                'value': context['item'].max_cp,
                'name': _('Max CP'),
                'percent': (context['item'].max_cp / django_settings.POKEMONS_MAX_STATS['max_cp']) * 100,
            }),
            ('catch_rate', {
                'value': context['item'].catch_rate,
                'name': _('Catch Rate'),
                'percent': (context['item'].catch_rate / django_settings.POKEMONS_MAX_STATS['catch_rate']) * 100,
                'suffix': '%',
            }),
            ('flee_rate', {
                'value': context['item'].flee_rate,
                'name': _('Flee Rate'),
                'percent': (context['item'].flee_rate / django_settings.POKEMONS_MAX_STATS['flee_rate']) * 100,
                'suffix': '%',
            }),
        ]),
    ]
    context['tab'] = 'collection'
    if 'tab' in request.GET and request.GET['tab'] in _full_pokemon_tabs:
        context['tab'] = request.GET['tab']
    if context['tab'] == 'collection':
        if request.user.is_authenticated():
            request.user.all_accounts = request.user.accounts.all().prefetch_related(
                Prefetch('pokedex', queryset=models.Pokedex.objects.filter(pokemon_id=context['item'].id), to_attr='in_pokedex'),
                Prefetch('pokemons', queryset=models.OwnedPokemon.objects.filter(pokemon_id=context['item'].id).order_by('-cp'), to_attr='all_pokemons'),
            )
            for account in request.user.all_accounts:
                if len(account.in_pokedex):
                    account.in_pokedex = account.in_pokedex[0]
                else:
                    account.in_pokedex = models.Pokedex.objects.create(account=account, pokemon=context['item'])
    elif context['tab'] == 'evolutions':
        pass
    elif context['tab'] == 'attacks':
        context['item'].all_attacks = context['item'].attacks.all().order_by('is_special')

############################################################
# OwnedPokemons

def ownedPokemonRedirectAfter(request, item, ajax=False):
    if ajax:
        return '/ajax/pokemon/{}/'.format(item.pokemon_id)
    if 'back_to_profile' in request.GET:
        return item.cached_account.owner.item_url
    return item.cached_pokemon.item_url

def foreachOwnedPokemon(index, item, context):
    item.is_mine = context['request'].user.id == item.cached_account.owner.id

def ownedPokemonsExtraContext(context):
    request = context['request']
    context['back_to_profile'] = 'back_to_profile' in request.GET

############################################################
# Attacks

def attacksExtraContext(context):
    context['pokemon_types'] = models.POKEMON_TYPES_DICT
