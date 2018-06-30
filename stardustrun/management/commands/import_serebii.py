import time, urllib2
from pprint import pprint
from bs4 import BeautifulSoup, Comment
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings as django_settings
from django.core.files.temp import NamedTemporaryFile
from django.core.files.images import ImageFile
from django.core.exceptions import ObjectDoesNotExist
from tinypng import shrink_file
from web.models import UserPreferences
from web.utils import join_data
from web.tools import totalDonators
from stardustrun import models

def shrunkImage(picture, filename):
    api_key = django_settings.TINYPNG_API_KEY
    if not api_key or not filename.endswith('.png'):
        return picture
    img_shrunked = NamedTemporaryFile(delete=False)
    shrink_info = shrink_file(
        picture.name,
        api_key=api_key,
        out_filepath=img_shrunked.name
    )
    img_shrunked.flush()
    return ImageFile(img_shrunked)

def downloadImageFile(url):
    img_temp = NamedTemporaryFile(delete=True)
    req = urllib2.Request(url, headers={ 'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/40.0.2214.94 Safari/537.36' })
    img_temp.write(urllib2.urlopen(req).read())
    img_temp.flush()
    return ImageFile(img_temp)

def downloadImage(url, tinypng=False):
    downloaded = downloadImageFile(url)
    if tinypng:
        return shrunkImage(downloaded, url)
    return downloaded

statsDB = {
    'Hit Points': 'hit_points',
    'Attack': 'attack',
    'Defense': 'defense',
    'Max CP': 'max_cp',
    'Catch Rate': 'catch_rate',
    'Flee Rate': 'flee_rate',
}

def import_serebii(args):

    if 'local' in args:
        f = open('pokemons.html', 'r')
    else:
        f = urllib2.urlopen('http://serebii.net/pokemongo/pokemon.shtml')

    try:
        owner = models.User.objects.get(username='db0')
    except ObjectDoesNotExist:
        owner = models.User.objects.create(username='db0')
        preferences = UserPreferences.objects.create(user=owner)
    soup = BeautifulSoup(f.read(), 'html5lib')
    pokemon_table = soup.find_all('table', {'class': 'tab', 'align': 'center'})[1]
    trs = pokemon_table.find_all('tr')
    evolutions = []
    evolution_of = None
    previous_id = 0
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) == 21:
            data = {
                'owner': owner,
                'evolution_of': evolution_of,
            }
            id = int(tds[0].text.strip().replace('#', ''))
            if previous_id == id:
                print '!!! Not adding duplicate', tds[3].text.strip()
            image = tds[1].find('img')
            image = 'http://serebii.net' + image.get('src')
            if 'noimages' not in args:
                # Check if pokemon already has an image before downloading it
                try:
                    pokemon = models.Pokemon.objects.get(id=id)
                except models.Pokemon.DoesNotExist:
                    pokemon = None
                if not pokemon or not pokemon.image:
                    data['image'] = downloadImage(image, True)
            i = tds[3].find_all('i')
            if i:
                if i[0].text == 'Not currently available':
                    data['is_available'] = False
                i[0].extract()
            data['name'] = tds[3].text.strip()
            types = []
            for image in tds[4].find_all('img'):
                types.append(image.get('src').strip().replace('/pokedex-bw/type/', '').replace('.gif', ''))
            data['types_string'] = join_data(*types)
            i = 6
            for stats_tr in tds[5].find_all('tr'):
                stat_tds = stats_tr.find_all('td')
                key = stat_tds[0].text
                value = int(stat_tds[1].text.replace('%', ''))
                if key in statsDB:
                    data[statsDB[key]] = value
                i += 2
            # Information about evolution candies not listed under cerebi anymore
            candies = tds[i].text.strip()
            for choice in dict(models.CANDIES_CHOICES).keys():
                if candies.startswith(str(choice)):
                    data['evolution_candies'] = choice
                    break
            #i += 1
            egg = tds[i].text.strip()
            if egg != 'Not in Eggs':
                for choice in dict(models.EGGS_CHOICES).keys():
                    if egg.startswith(str(choice)):
                        data['egg_distance'] = choice
                        break
            i = i + 1
            all_attacks = []
            attacks = tds[i].find_all('a')
            for attack in attacks:
                attack = attack.text.strip()
                attack, _ = models.Attack.objects.get_or_create(name=attack)
                all_attacks.append(attack)
            i = i + 1
            special_attacks = tds[i].find_all('a')
            for attack in special_attacks:
                attack = attack.text.strip()
                attack, _ = models.Attack.objects.get_or_create(name=attack, defaults={ 'is_special': True })
                all_attacks.append(attack)
            pokemon, _ = models.Pokemon.objects.update_or_create(id=id, defaults=data)
            current_attacks = pokemon.attacks.all()
            for attack in all_attacks:
                if attack not in current_attacks:
                    pokemon.attacks.add(attack)
            pokemon.save()
            if pokemon.evolution_candies:
                evolution_of = pokemon
            else:
                evolution_of = None
            print u'Added #{} {}'.format(pokemon.id, pokemon.name)
            previous_id = pokemon.id
    print 'Manually set evolution for other evee evolutions'
    models.Pokemon.objects.filter(pk__in=[134, 135, 136]).update(evolution_of_id=133)

    if 'local' in args:
        f = open('pokemonattacks.html', 'r')
    else:
        f = urllib2.urlopen('http://serebii.net/pokemongo/moves.shtml')

    soup = BeautifulSoup(f.read(), 'html5lib')
    trs = soup.find_all('tr')
    for tr in trs:
        tds = tr.find_all('td')
        if len(tds) == 6 or len(tds) == 7:
            name = tds[0].text.strip()
            if name == 'Name':
                continue
            data = {
                'is_special': len(tds) == 7,
            }
            data['type'] = tds[1].find('img').get('src').strip().replace('/pokedex-bw/type/', '').replace('.gif', '')
            data['damage'] = int(tds[2].text.strip() or '0')
            data['duration'] = float(tds[4].text.replace('seconds', '').strip())
            if data['is_special']:
                data['critical_hit_chance'] = int(tds[3].text.replace('%', '').strip())
                try:
                    data['energy_requirement'] = int(tds[5].find('img').get('src').strip().replace('energy.png', ''))
                except AttributeError:
                    pass
            else:
                data['energy_increase'] = int(tds[3].text.strip())
            attack, created = models.Attack.objects.update_or_create(name=name, defaults=data)
            print u'{} {}'.format('Added' if created else '    ', name)

class Command(BaseCommand):
    can_import_settings = True

    def handle(self, *args, **options):
        import_serebii(args)
