from django.db.models import Q
from django.core.exceptions import PermissionDenied

############################################################
# Pokemons

def filterPokemons(queryset, parameters, request):
    if request.user.is_authenticated():
        request.user.all_accounts = request.user.accounts.all()
        accounts_pks = ','.join([str(account.pk) for account in request.user.all_accounts])
        if accounts_pks:
            queryset = queryset.extra(select={
                'owned': 'SELECT COUNT(*) FROM stardustrun_ownedpokemon WHERE pokemon_id = stardustrun_pokemon.id AND account_id IN ({})'.format(accounts_pks),
                'seen': 'SELECT COUNT(*) FROM stardustrun_pokedex WHERE pokemon_id = stardustrun_pokemon.id AND account_id IN ({}) AND seen = 1'.format(accounts_pks),
            })
    if 'search' in parameters and parameters['search']:
        terms = parameters['search'].split(' ')
        for term in terms:
            queryset = queryset.filter(Q(name__icontains=term)
                                       | Q(types_string__icontains=term)
            )
    if 'type' in parameters and parameters['type']:
        queryset = queryset.filter(types_string__contains='"{}"'.format(parameters['type']))
    if 'is_available' in parameters and parameters['is_available']:
        if parameters['is_available'] == '2':
            queryset = queryset.filter(is_available=True)
        elif parameters['is_available'] == '3':
            queryset = queryset.filter(is_available=False)
    if request.user.is_authenticated():
        if 'owned' in parameters and parameters['owned']:
            if parameters['owned'] == '2':
                queryset = queryset.filter(have_it__account__owner_id=request.user.id)
            elif parameters['owned'] == '3':
                queryset = queryset.exclude(have_it__account__owner_id=request.user.id)
        if 'seen' in parameters and parameters['seen']:
            if parameters['seen'] == '2':
                queryset = queryset.filter(pokedexes__account__owner_id=request.user.id, pokedexes__seen=True)
            elif parameters['seen'] == '3':
                queryset = queryset.exclude(pokedexes__account__owner_id=request.user.id, pokedexes__seen=True)
    if 'attack' in parameters:
        queryset = queryset.filter(attacks__id=parameters['attack'])
    if 'ordering' in parameters and parameters['ordering'] == 'evolution_candies':
        queryset = queryset.filter(evolution_candies__isnull=False)
    if 'ordering' in parameters and parameters['ordering'] == 'egg_distance':
        queryset = queryset.filter(egg_distance__isnull=False)
    if 'ids' in parameters and parameters['ids']:
        queryset = queryset.filter(id__in=parameters['ids'].split(','))
    return queryset

############################################################
# OwnedPokemons

def filterOwnedPokemons(queryset, parameters, request):
    if 'account' in parameters:
        queryset = queryset.filter(account_id=parameters['account'])
    elif 'ids' in parameters and parameters['ids']:
        queryset = queryset.filter(id__in=parameters['ids'].split(','))
    else:
        raise PermissionDenied()
    if 'search' in parameters and parameters['search']:
        terms = parameters['search'].split(' ')
        for term in terms:
            queryset = queryset.filter(Q(pokemon__name__icontains=term)
                                       | Q(pokemon__types_string__icontains=term)
                                       | Q(nickname__icontains=term)
            )
    if 'type' in parameters and parameters['type']:
        queryset = queryset.filter(pokemon__types_string__contains='"{}"'.format(parameters['type']))
    return queryset

############################################################
# Accounts

def filterAccounts(queryset, parameters, request):
    if 'search' in parameters and parameters['search']:
        terms = parameters['search'].split(' ')
        for term in terms:
            queryset = queryset.filter(Q(nickname__icontains=term)
                                       | Q(team__icontains=term)
                                       | Q(owner__username__icontains=term)
                                       | Q(owner__email__iexact=term)
            )
    if 'team' in parameters and parameters['team']:
        queryset = queryset.filter(team=parameters['team'])
    if 'starter_id' in parameters and parameters['starter_id']:
        queryset = queryset.filter(starter_id=parameters['starter_id'])
    return queryset

############################################################
# Attacks

def filterAttacks(queryset, parameters, request):
    if 'search' in parameters and parameters['search']:
        terms = parameters['search'].split(' ')
        for term in terms:
            queryset = queryset.filter(name__icontains=term)
    if 'type' in parameters and parameters['type']:
        queryset = queryset.filter(type=parameters['type'])
    if 'is_special' in parameters and parameters['is_special']:
        if parameters['is_special'] == '2':
            queryset = queryset.filter(is_special=True)
        elif parameters['is_special'] == '3':
            queryset = queryset.filter(is_special=False)
    if 'ordering' in parameters and parameters['ordering'] == 'energy_increase':
        queryset = queryset.filter(energy_increase__isnull=False)
    if 'ordering' in parameters and parameters['ordering'] == 'critical_hit_chance':
        queryset = queryset.filter(critical_hit_chance__isnull=False)
    if 'ordering' in parameters and parameters['ordering'] == 'energy_requirement':
        queryset = queryset.filter(energy_requirement__isnull=False)
    return queryset
