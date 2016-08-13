import time
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings as django_settings
from web.tools import totalDonators
from stardustrun import models

def generate_settings():

    print 'Get total donators'
    total_donators = totalDonators()

    print 'Get the characters'
    all_pokemons = models.Pokemon.objects.all().order_by('id')
    favorite_characters = [(
        pokemon.pk,
        pokemon.name,
        pokemon.image_url,
    ) for pokemon in all_pokemons]

    print 'Get the starters'
    starters = models.Pokemon.objects.filter(pk__in=[1,4,7,25])
    starters_images = [(pokemon.id, pokemon.image_url) for pokemon in starters]
    starters = [(pokemon.id, pokemon.name) for pokemon in starters]

    print 'Get max stats'
    stats = { 'max_cp': None, 'hit_points': None, 'attack': None, 'defense': None, 'catch_rate': None, 'flee_rate': None }
    for stat in stats.keys():
        max_pokemon = models.Pokemon.objects.order_by('-' + stat)[0]
        stats[stat] = getattr(max_pokemon, stat)

    print 'Save generated settings'
    s = u'\
import datetime\n\
from django.utils.translation import ugettext_lazy as _\n\
TOTAL_DONATORS = ' + unicode(total_donators) + u'\n\
ALL_POKEMONS = ' + unicode(favorite_characters) + u'\n\
ALL_POKEMONS_DICT = {pk:{\'name\':name,\'image\':image} for (pk,name,image) in ALL_POKEMONS}\n\
STARTERS = ' + unicode(starters) + u'\n\
STARTERS_IMAGES = ' + unicode(starters_images) + u'\n\
POKEMONS_MAX_STATS = ' + unicode(stats) + '\n\
GENERATED_DATE = datetime.datetime.fromtimestamp(' + unicode(time.time()) + u')\n\
'
    print s
    filename = django_settings.BASE_DIR + '/' + django_settings.SITE + '_project/generated_settings.py'
    print filename
    f = open(filename, 'w')
    print >> f, s
    f.close()

class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        generate_settings()
