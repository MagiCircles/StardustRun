from django.http import JsonResponse
from django.core.exceptions import PermissionDenied
from django.shortcuts import render, get_object_or_404, redirect
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_exempt
from django.utils.translation import ugettext_lazy as _
from django.conf import settings as django_settings
from web.tools import itemURL
from web.views_collections import item_view
from stardustrun.settings import ENABLED_COLLECTIONS
from stardustrun.utils import globalContext
from stardustrun import models, forms

############################################################
# Ajax - Pokedex displayed in profile accounts tabs

def _createMultiplePokedexes(account, pokemons_ids):
    models.Pokedex.objects.bulk_create([
        models.Pokedex(account=account, pokemon_id=id)
        for id in pokemons_ids])

def pokedex(request, account):
    context = globalContext(request)
    all_pokemons = { p[0] : None for p in django_settings.ALL_POKEMONS }
    account = get_object_or_404(models.Account, pk=account)
    pokedexes = models.Pokedex.objects.filter(account=account).select_related('pokemon')
    for pokedex in pokedexes:
        all_pokemons[pokedex.pokemon_id] = pokedex
    pokedexes_to_create = [id for (id, pokedex) in all_pokemons.items() if not pokedex]
    if pokedexes_to_create:
        _createMultiplePokedexes(account, pokedexes_to_create)
        new_pokedexes = models.Pokedex.objects.filter(account=account, pokemon_id__in=pokedexes_to_create).select_related('pokemon')
        for pokedex in new_pokedexes:
            all_pokemons[pokedex.pokemon_id] = pokedex
    context['pokedexes'] = all_pokemons.values()
    sorted(context['pokedexes'], key=lambda p: p.pokemon_id)
    context['js_files'] = ['full_pokemon']
    context['account'] = account
    context['hide_account'] = True
    context['not_editable'] = account.owner_id != request.user.id
    context['view'] = request.GET.get('view', 'icons' if context['not_editable'] else 'list')
    return render(request, 'pages/ajax_pokedex.html', context)

############################################################
# Evolve form for ownedpokemons

def evolve(request, ownedpokemon):
    context = globalContext(request)
    ownedpokemon = get_object_or_404(models.OwnedPokemon.objects.select_related('pokemon'), pk=ownedpokemon, account__owner_id=request.user.id)
    ajax = context['current'].endswith('_ajax')
    if not ownedpokemon.pokemon.next_evolutions_ids:
        return redirect(itemURL(ownedpokemon.pokemon, ajax=ajax))
    if request.method == 'POST' and 'evolve' in request.POST:
        form = forms.EvolveOwnedPokemonForm(request.POST, instance=ownedpokemon)
        if form.is_valid():
            instance = form.save()
            if not ajax and 'back_to_profile' in request.GET:
                return redirect(itemURL('user', request.user))
            return redirect(itemURL('pokemon', instance.pokemon, ajax=ajax))
    else:
        form = forms.EvolveOwnedPokemonForm(instance=ownedpokemon)
    context['op'] = ownedpokemon
    context['forms'] = { 'evolve': form }
    context['ajax'] = ajax
    context['evolution_data'] = [
        (id, django_settings.ALL_POKEMONS_DICT[id])
        for id in ownedpokemon.pokemon.flatten_next_evolutions_ids
    ]
    context['js_files'] = ['evolve']
    if ajax:
        context['extends'] = 'ajax.html'
    return render(request, 'pages/evolve.html', context)

############################################################
# Ajax - Add ownedpokemon to collection

def add_pokemon(request, pokemon):
    if request.method != 'POST' or 'account' not in request.POST:
        raise PermissionDenied()
    pokemon = get_object_or_404(models.Pokemon, pk=pokemon)
    account = get_object_or_404(models.Account.objects.filter(owner=request.user), pk=request.POST['account'])
    if 'get_started' in request.GET:
        try:
            models.Pokedex.objects.create(pokemon=pokemon, account=account, seen=True, caught=True)
        except IntegrityError:
            models.Pokedex.objects.filter(pokemon=pokemon, account=account).update(seen=True, caught=True)
    else:
        updated = models.Pokedex.objects.filter(pokemon=pokemon, account=account).update(seen=True, caught=True)
        if not updated:
            models.Pokedex.objects.create(pokemon=pokemon, account=account, seen=True, caught=True)
    ownedpokemon = models.OwnedPokemon.objects.create(account=account, pokemon=pokemon)
    if 'full-pokemon' in request.GET:
        return item_view(request, 'pokemon', ENABLED_COLLECTIONS['pokemon'], pk=ownedpokemon.pokemon.id, item=pokemon, ajax=True)
    return JsonResponse({
        'added': True,
    })

############################################################
# Ajax - Change pokedex: candies, seen and caught

def change_candies(request, pokemon, account):
    if request.method != 'POST' or 'candies' not in request.POST:
        raise PermissionDenied()
    pokedex = get_object_or_404(models.Pokedex, account_id=account, account__owner=request.user, pokemon_id=pokemon)
    pokedex.candies = int(request.POST['candies'])
    if pokedex.candies < 0:
        pokedex.candies = 0
    updated = models.Pokedex.objects.filter(account_id=account, pokemon__id__in=pokedex.cached_evolution_chain).update(candies=pokedex.candies)
    if updated != len(pokedex.cached_evolution_chain):
        for id in pokedex.cached_evolution_chain:
            if id != pokedex.pokemon_id:
                try: models.Pokedex.objects.create(pokemon_id=id, account_id=account, candies=pokedex.candies)
                except IntegrityError: pass
    return JsonResponse({
        'candies': pokedex.candies,
        'seen': pokedex.seen,
        'caught': pokedex.caught,
        'updated': pokedex.cached_evolution_chain,
    })

def _pokedexError(request, pokedex):
    return JsonResponse({
        'error': _('You have {} of them in you collection. Delete them before changing this.').format(pokedex.total_caught),
    })

def _pokedexReturn(pokedex):
    return JsonResponse({
        'candies': pokedex.candies,
        'seen': pokedex.seen,
        'caught': pokedex.caught,
        'updated': [pokedex.id],
    })

def _getPokedexWithCaught(request, pokemon, account):
    return get_object_or_404(
        models.Pokedex.objects.extra(select={
            'total_caught': 'SELECT COUNT(*) FROM stardustrun_ownedpokemon WHERE pokemon_id = {pokemon_id} AND account_id = {account_id}'.format(pokemon_id=int(pokemon), account_id=int(account))
        }),
        account_id=account, account__owner=request.user, pokemon_id=pokemon)

@csrf_exempt
def change_caught(request, pokemon, account):
    if request.method != 'POST' or 'caught' not in request.POST:
        raise PermissionDenied()
    pokedex = _getPokedexWithCaught(request, pokemon, account)
    pokedex.caught = request.POST['caught'] == 'true'
    if not pokedex.caught and pokedex.total_caught:
        return _pokedexError(request, pokedex)
    if pokedex.caught:
        pokedex.seen = True
    pokedex.save()
    return _pokedexReturn(pokedex)

@csrf_exempt
def change_seen(request, pokemon, account):
    if request.method != 'POST' or 'seen' not in request.POST:
        raise PermissionDenied()
    pokedex = _getPokedexWithCaught(request, pokemon, account)
    pokedex.seen = request.POST['seen'] == 'true'
    if not pokedex.seen and pokedex.total_caught:
        return _pokedexError(request, pokedex)
    if not pokedex.seen:
        pokedex.caught = False
    pokedex.save()
    return _pokedexReturn(pokedex)

############################################################
# Ajax - Qucik Level Up button on profile

def level_up(request, account):
    account = get_object_or_404(models.Account.objects.filter(owner=request.user), pk=account)
    account.level += 1
    account.update_cache_leaderboards()
    account.save()
    return JsonResponse({
        'level': account.level,
        'leaderboard': account.cached_leaderboard,
        'leaderboard_team': account.cached_leaderboard_team,
    })
