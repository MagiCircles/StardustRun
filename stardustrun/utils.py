from web.utils import globalContext as web_globalContext
from stardustrun import models

def globalContext(request):
    context = web_globalContext(request)
    return context

def onUserEdited(request):
    accounts = models.Account.objects.filter(owner_id=request.user.id).select_related('owner', 'owner__preferences')
    for account in accounts:
        account.force_cache()
    ownedPokemons = models.OwnedPokemon.objects.filter(account__owner_id=request.user.id).select_related('pokemon', 'account', 'attack', 'special_attack')
    for op in ownedPokemons:
        op.force_cache()

def onPreferencesEdited(request):
    accounts = models.Account.objects.filter(owner_id=request.user.id).select_related('owner', 'owner__preferences')
    for account in accounts:
        account.force_cache()
