# -*- coding: utf-8 -*-
import datetime, os
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _
from django.conf import settings as django_settings
from django.db import models
from web.utils import split_data, join_data, AttrDict, tourldash
from stardustrun.model_choices import *

############################################################
# Attack

class Attack(models.Model):
    name = models.CharField(max_length=100, unique=True)
    type = models.CharField(max_length=100, choices=POKEMON_TYPES_DATABASE_CHOICES)
    damage = models.PositiveIntegerField(_('Damage'), null=True)
    energy_increase = models.PositiveIntegerField(_('Energy Increase'), null=True)
    critical_hit_chance = models.PositiveIntegerField(_('Critical Hit Chance'), null=True)
    duration = models.FloatField(_('Duration'), null=True)
    energy_requirement = models.PositiveIntegerField(_('Energy Requirement'), null=True)
    is_special = models.BooleanField(default=False)

    @property
    def type_data(self):
        return POKEMON_TYPES_DICT[self.type if self.type else 'normal']

    def __unicode__(self):
        return self.name

############################################################
# Pokemon

def pokemonUploadTo(instance, filename):
    _, extension = os.path.splitext(filename)
    if not extension:
        extension = '.png'
    return django_settings.STATIC_UPLOADED_FILES_PREFIX + 'p/' + unicode(instance.id) + tourldash(instance.name) + extension

class Pokemon(models.Model):
    id = models.PositiveIntegerField(_(u'Pokémon number'), unique=True, primary_key=True)
    name = models.CharField(_(u'Pokémon name'), max_length=100, unique=True)
    image = models.ImageField(_('Image'), upload_to=pokemonUploadTo)
    owner = models.ForeignKey(User, related_name='created_pokemons')
    is_available = models.BooleanField(_('Available'), default=True)
    types_string = models.TextField(_('Types'), blank=True, null=True)
    hit_points = models.PositiveIntegerField(_('Hit Points'), null=True)
    attack = models.PositiveIntegerField(_('Attack'), null=True)
    defense = models.PositiveIntegerField(_('Defense'), null=True)
    max_cp = models.PositiveIntegerField(_('Max CP'), null=True)
    catch_rate = models.PositiveIntegerField(_('Catch Rate'), null=True)
    flee_rate = models.PositiveIntegerField(_('Flee Rate'), null=True)
    evolution_of = models.ForeignKey('self', related_name='evolutions', null=True, on_delete=models.SET_NULL)
    evolution_candies = models.PositiveIntegerField(_('Candies needed to evolve'), null=True, choices=CANDIES_CHOICES)
    egg_distance = models.PositiveIntegerField(_('Egg Distance'), null=True, choices=EGGS_CHOICES)
    attacks = models.ManyToManyField(Attack, related_name='pokemons_with_attack')

    # Cache
    _cache_previous_evolutions = models.TextField(blank=True, null=True)
    _cache_next_evolutions = models.TextField(blank=True, null=True)

    def force_cache(self):
        all_previous = []
        previous = self.evolution_of
        while previous:
            all_previous.append(unicode(previous.pk))
            previous = previous.evolution_of
        all_previous.reverse()
        self._cache_previous_evolutions = join_data(*all_previous)
        if not self._cache_previous_evolutions:
            self._cache_previous_evolutions = ''
        next = self.evolutions.all()
        all_next = []
        while len(next):
            all_next.append('-'.join([unicode(p.pk) for p in next]))
            next = next[0].evolutions.all() if len(next) else None
        self._cache_next_evolutions = join_data(*all_next)
        if not self._cache_next_evolutions:
            self._cache_next_evolutions = ''
        self.save()

    def invalidate_cache(self):
        self._cache_previous_evolutions = None
        self._cache_next_evolutions = None

    @property
    def previous_evolutions_ids(self):
        if self._cache_previous_evolutions is None:
            self.force_cache()
        return [int(e) for e in split_data(self._cache_previous_evolutions)]

    @property
    def next_evolutions_ids(self):
        if self._cache_next_evolutions is None:
            self.force_cache()
        return [[int(m) for m in n.split('-')] if '-' in n else int(n) for n in split_data(self._cache_next_evolutions)]

    @property
    def flatten_next_evolutions_ids(self):
        flatten = []
        for n in self.next_evolutions_ids:
            if isinstance(n, list):
                flatten += n
            else:
                flatten.append(n)
        return flatten

    @property
    def evolution_chain_ids(self):
        return self.previous_evolutions_ids + [self.id] + self.next_evolutions_ids

    @property
    def flatten_evolution_chain_ids(self):
        return self.previous_evolutions_ids + [self.id] + self.flatten_next_evolutions_ids

    @property
    def get_evolution_chain(self):
        if not hasattr(self, '_local_cache_evolution_chain'):
            self._local_cache_evolution_chain = getPokemonEvolutionChain(self)
        return self._local_cache_evolution_chain

    @property
    def get_flatten_evolution_chain(self):
        if not hasattr(self, '_local_cache_flatten_evolution_chain'):
            self._local_cache_flatten_evolution_chain = getFlattenPokemonEvolutionChain(self)
        return self._local_cache_flatten_evolution_chain

    @property
    def cached_owner(self):
        if not self._cache_last_update or self._cache_last_update < timezone.now() - datetime.timedelta(days=self._cache_days):
            self.force_cache()
        return AttrDict({
            'pk': self.owner_id,
            'id': self.owner_id,
            'username': self._cache_owner_username,
            'email': self._cache_owner_email,
            'item_url': '/user/{}/{}/'.format(self.owner_id, self._cache_owner_username),
            'preferences': AttrDict({
                'status': self._cache_owner_preferences_status,
                'twitter': self._cache_owner_preferences_twitter,
            }),
        })

    @property
    def types(self):
        return split_data(self.types_string)

    @property
    def types_data(self):
        return { type: POKEMON_TYPES_DICT[type] for type in self.types }

    @property
    def main_type(self):
        try:
            return self.types[0]
        except IndexError:
            return 'normal'

    @property
    def secondary_type(self):
        try:
            return self.types[1]
        except IndexError:
            return self.main_type

    @property
    def main_type_data(self):
        return POKEMON_TYPES_DICT[self.main_type]

    @property
    def secondary_type_data(self):
        return POKEMON_TYPES_DICT[self.secondary_type]

    def save_types(self, types):
        self.types_string = join_data(*types)

    @property
    def egg_distance_text(self):
        return dict(EGGS_CHOICES)[self.egg_distance] if self.egg_distance else None

    def __unicode__(self):
        return self.name

def getFlattenPokemonEvolutionChain(pokemon):
    return { p.pk: p for p in Pokemon.objects.filter(pk__in=pokemon.flatten_evolution_chain_ids) }

def getPokemonEvolutionChain(pokemon):
    pokemons = getFlattenPokemonEvolutionChain(pokemon)
    chain = []
    for e in pokemon.evolution_chain_ids:
        if isinstance(e, list):
            chain.append([pokemons[p] for p in e])
        else:
            chain.append([pokemons[e]])
    return chain

############################################################
# Account

class Account(models.Model):
    owner = models.ForeignKey(User, related_name='accounts', db_index=True)
    creation = models.DateTimeField(auto_now_add=True)
    nickname = models.CharField(_("Nickname"), max_length=20)
    level = models.PositiveIntegerField(_('Level'), null=True, db_index=True)
    team = models.CharField(_('Team'), max_length=10, choices=TEAM_DATABASE_CHOICES, null=True)
    starter = models.ForeignKey(Pokemon, related_name='accouts_started_with', on_delete=models.SET_NULL, null=True)
    start_date = models.DateField(null=True, verbose_name=_('Start Date'), help_text=_('When you started playing with this account.'))
    bought_coins = models.PositiveIntegerField(_(u'Bought Pokécoins'), null=True)
    stardust = models.PositiveIntegerField(_(u'Stardust'), null=True)
    lucky_eggs = models.PositiveIntegerField(_(u'Lucky Eggs'), null=True)
    incenses = models.PositiveIntegerField(_(u'Incenses'), null=True)
    lure_modules = models.PositiveIntegerField(_(u'Lure Modules'), null=True)

    # Cache
    _cache_days = 20
    _cache_last_update = models.DateTimeField(null=True)
    _cache_owner_username = models.CharField(max_length=32, null=True)
    _cache_owner_email = models.EmailField(blank=True)
    _cache_owner_preferences_status = models.CharField(choices=DONATORS_STATUS_CHOICES, max_length=12, null=True)
    _cache_owner_preferences_twitter = models.CharField(max_length=32, null=True, blank=True)

    _cache_leaderboards_days = 3
    _cache_leaderboards_last_update = models.DateTimeField(null=True)
    _cache_leaderboard = models.PositiveIntegerField(null=True)
    _cache_leaderboard_team = models.PositiveIntegerField(null=True)

    def update_cache_leaderboards(self):
        self._cache_leaderboard = getAccountLeaderboard(self)
        self._cache_leaderboard_team = getAccountLeaderboardForTeam(self)

    def force_cache_leaderboards(self):
        self._cache_leaderboards_last_update = timezone.now()
        self.update_cache_leaderboards()
        self.save()

    def invalidate_cache_leaderboards(self):
        self._cache_leaderboards_last_update = None

    def force_cache(self):
        """
        Recommended to use select_related('owner', 'owner__preferences') when calling this method
        """
        self._cache_last_update = timezone.now()
        self._cache_owner_username = self.owner.username
        self._cache_owner_email = self.owner.email
        self._cache_owner_preferences_status = self.owner.preferences.status
        self._cache_owner_preferences_twitter = self.owner.preferences.twitter
        self.save()

    def invalidate_cache(self):
        self._cache_last_update = None

    @property
    def cached_owner(self):
        if not self._cache_last_update or self._cache_last_update < timezone.now() - datetime.timedelta(days=self._cache_days):
            self.force_cache()
        return AttrDict({
            'pk': self.owner_id,
            'id': self.owner_id,
            'username': self._cache_owner_username,
            'email': self._cache_owner_email,
            'item_url': '/user/{}/{}/'.format(self.owner_id, self._cache_owner_username),
            'preferences': AttrDict({
                'status': self._cache_owner_preferences_status,
                'twitter': self._cache_owner_preferences_twitter,
            }),
        })

    @property
    def cached_starter(self):
        return AttrDict({
            'pk': self.starter_id,
            'id': self.starter_id,
            'name': dict(django_settings.STARTERS)[self.starter_id],
            'image': dict(django_settings.STARTERS_IMAGES)[self.starter_id],
            'item_url': '/pokemon/{}/{}/'.format(self.starter_id, tourldash(dict(django_settings.STARTERS)[self.starter_id])),
            'ajax_item_url': '/ajax/pokemon/{}/'.format(self.starter_id),
        })

    @property
    def localizedTeam(self):
        return dict(TEAM_CHOICES)[self.team]

    @property
    def items(self):
        return {
            item: {
                'value': getattr(self, item),
                'name': name,
            } for (item, name) in {
                'stardust': _('Stardust'),
                'lucky_eggs': _('Lucky Eggs'),
                'incenses': _('Incenses'),
                'lure_modules': _('Lure Modules'),
            }.items()
            if getattr(self, item) > 0
        }

    @property
    def money_spent(self):
        return int(round(self.bought_coins * 0.007))

    @property
    def cached_leaderboard(self):
        if not self._cache_leaderboards_last_update or self._cache_leaderboards_last_update < timezone.now() - datetime.timedelta(days=self._cache_leaderboards_days):
            self.force_cache_leaderboards()
        return self._cache_leaderboard

    @property
    def cached_leaderboard_team(self):
        if not self._cache_leaderboards_last_update or self._cache_leaderboards_last_update < timezone.now() - datetime.timedelta(days=self._cache_leaderboards_days):
            self.force_cache_leaderboards()
        return self._cache_leaderboard_team

    def __unicode__(self):
        return u'{} Lv. {}'.format(self.nickname, self.level)

def getAccountLeaderboard(account):
    return Account.objects.filter(level__gt=account.level).values('level').distinct().count() + 1

def getAccountLeaderboardForTeam(account):
    if not account.team:
        return None
    return Account.objects.filter(team=account.team, level__gt=account.level).values('level').distinct().count() + 1

############################################################
# OwnedPokemon

class OwnedPokemon(models.Model):
    account = models.ForeignKey(Account, related_name='pokemons', db_index=True)
    pokemon = models.ForeignKey(Pokemon, related_name='have_it', db_index=True)
    cp = models.PositiveIntegerField(_('CP'), null=True)
    hp = models.PositiveIntegerField(_('HP'), null=True)
    weight = models.FloatField(_('Weight'), null=True)
    height = models.FloatField(_('Height'), null=True)
    attack = models.ForeignKey(Attack, null=True, related_name='owned_pokemon_attack', on_delete=models.SET_NULL, verbose_name=_('Attack'))
    special_attack = models.ForeignKey(Attack, null=True, related_name='owned_pokemon_special_attack', on_delete=models.SET_NULL, verbose_name=_('Special Attack'))
    nickname = models.CharField(_("Nickname"), max_length=20, null=True)

    # Cache
    _cache_days = 20
    _cache_last_update = models.DateTimeField(null=True)
    _cache_account_nickname = models.CharField(max_length=20, null=True)
    _cache_account_owner_id = models.PositiveIntegerField(null=True)
    _cache_account_owner_username = models.CharField(max_length=32, null=True)
    _cache_attack_name = models.CharField(max_length=100, null=True)
    _cache_special_attack_name = models.CharField(max_length=100, null=True)
    _cache_can_evolve = models.NullBooleanField(default=None)
    _cache_max_cp = models.PositiveIntegerField(null=True)

    def force_cache(self):
        """
        Recommended to use select_related('pokemon', 'account', 'attack', 'special_attack') when calling this method
        """
        self._cache_last_update = timezone.now()
        self._cache_account_nickname = self.account.nickname
        self._cache_account_owner_id = self.account.owner_id
        self._cache_account_owner_username = self.account.cached_owner.username
        if self.attack_id:
            self._cache_attack_name = self.attack.name
        if self.special_attack_id:
            self._cache_special_attack_name = self.special_attack.name
        self._cache_can_evolve = bool(self.pokemon.flatten_next_evolutions_ids)
        self._cache_max_cp = self.pokemon.max_cp
        self.save()

    def invalidate_cache(self):
        self._cache_last_update = None

    @property
    def cached_account(self):
        if not self._cache_last_update or self._cache_last_update < timezone.now() - datetime.timedelta(days=self._cache_days):
            self.force_cache()
        return AttrDict({
            'pk': self.account_id,
            'id': self.account_id,
            'nickname': self._cache_account_nickname,
            'owner_id': self._cache_account_owner_id,
            'item_url': '/user/{}/{}/'.format(self._cache_account_owner_id, self._cache_account_owner_username),
            'owner': AttrDict({
                'id': self._cache_account_owner_id,
                'pk': self._cache_account_owner_id,
                'username': self._cache_account_owner_username,
                'item_url': '/user/{}/{}/'.format(self._cache_account_owner_id, self._cache_account_owner_username),
            }),
        })

    @property
    def cached_attack(self):
        if not self.attack_id:
            return None
        if not self._cache_last_update or self._cache_last_update < timezone.now() - datetime.timedelta(days=self._cache_days):
            self.force_cache()
        return AttrDict({
            'pk': self.attack_id,
            'id': self.attack_id,
            'name': self._cache_attack_name,
        })

    @property
    def cached_special_attack(self):
        if not self.special_attack_id:
            return None
        if not self._cache_last_update or self._cache_last_update < timezone.now() - datetime.timedelta(days=self._cache_days):
            self.force_cache()
        return AttrDict({
            'pk': self.attack_id,
            'id': self.attack_id,
            'name': self._cache_special_attack_name,
        })

    @property
    def cached_pokemon(self):
        pokemon = django_settings.ALL_POKEMONS_DICT[self.pokemon_id]
        return AttrDict({
            'pk': self.pokemon_id,
            'id': self.pokemon_id,
            'name': pokemon['name'],
            'image': pokemon['image'],
            'item_url': '/pokemon/{}/{}/'.format(self.pokemon_id, tourldash(pokemon['name'])),
            'ajax_item_url': '/ajax/pokemon/{}/'.format(self.pokemon_id),
        })

    @property
    def can_evolve(self):
        if self._cache_can_evolve is None:
            self.force_cache()
        return self._cache_can_evolve

    @property
    def max_cp(self):
        if self._cache_max_cp is None:
            self.force_cache()
        return self._cache_max_cp

    @property
    def force_nickname(self):
        if self.nickname:
            return self.nickname
        return _(self.cached_pokemon.name)

    @property
    def force_is_mine(self):
        self.is_mine = True

    @property
    def owner(self):
        return self.cached_account.owner

    @property
    def owner_id(self):
        return self.cached_account.owner.id

    def __unicode__(self):
        return u'{}'.format(self.force_nickname)

############################################################
# Pokedex

class Pokedex(models.Model):
    """
    For each account and pokemon, store weither you've seen/caught it + how many candies you have.
    """
    account = models.ForeignKey(Account, related_name='pokedex', db_index=True)
    pokemon = models.ForeignKey(Pokemon, related_name='pokedexes', db_index=True)
    candies = models.PositiveIntegerField(_('Candies'), default=0)
    seen = models.BooleanField(_('Seen'), default=False)
    caught = models.BooleanField(_('Caught'), default=False)

    # Cache
    _cache_evolution_chain = models.TextField(blank=True, null=True)

    def force_cache(self):
        """
        Recommended to use select_related('pokemon') when calling this method
        """
        chain = self.pokemon.flatten_evolution_chain_ids
        if 133 in chain:
            chain = Pokemon.objects.get(id=133).flatten_evolution_chain_ids
        self._cache_evolution_chain = join_data(*chain)
        if not self._cache_evolution_chain:
            self._cache_evolution_chain = ''
        self.save()

    def invalidate_cache(self):
        self._cache_evolution_chain = None

    @property
    def cached_evolution_chain(self):
        if self._cache_evolution_chain is None:
            self.force_cache()
        return [int(e) for e in split_data(self._cache_evolution_chain)]

    class Meta:
        unique_together = (('account', 'pokemon'),)

    def __unicode__(self):
        return 'Account #{} Pokedex for pokemon #{}'.format(self.account_id, self.pokemon_id)
