# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _

############################################################
# Accounts

TEAM_CHOICES = [
    ('instinct', _('Instinct'), 'instinct'),
    ('mystic', _('Mystic'), 'mystic'),
    ('valor', _('Valor'), 'valor'),
]

TEAM_DATABASE_CHOICES = [(raw, localized) for (raw, localized, css) in TEAM_CHOICES]

DONATORS_STATUS_CHOICES = [
    ('THANKS', ''),
    ('SUPPORTER', _(u'Pokémon Trainer')),
    ('LOVER', _(u'Super Pokémon Trainer')),
    ('AMBASSADOR', _(u'Expert Pokémon Trainer')),
    ('PRODUCER', _(u'Pokémon Master')),
    ('DEVOTEE', _(u'Ultimate Pokémon Master')),
]

############################################################
# Pokemons

EGGS_CHOICES = [
    (2, '2km'),
    (5, '5km'),
    (10, '10km'),
]

CANDIES_CHOICES = [
    (12, 12),
    (25, 25),
    (50, 50),
    (100, 100),
    (400, 400),
]

POKEMON_TYPES = [
    ('fairy', _('Fairy'), '#dba6dc', ['poison', 'steel'], ['fight', 'dragon', 'dark']),
    ('steel', _('Steel'), '#b9b7cd', ['fire', 'fight', 'ground'], ['ice', 'rock', 'fairy']),
    ('dark', _('Dark'), '#6a5345', ['fight', 'bug', 'fairy'], ['psychic', 'ghost']),
    ('dragon', _('Dragon'), '#6a32f3', ['ice', 'dragon', 'fairy'], ['dragon']),
    ('ghost', _('Ghost'), '#6f5697', ['ghost', 'dark'], ['psychic', 'ghost']),
    ('rock', _('Rock'), '#b6a434', ['water', 'grass', 'fight', 'ground', 'steel'], ['fire', 'ice', 'flying', 'bug']),
    ('bug', _('Bug'), '#a8b821', ['fire', 'flying', 'rock'], ['grass', 'psychic', 'dark']),
    ('psychic', _('Psychic'), '#f95789', ['bug', 'ghost', 'dark'], ['fight', 'poison']),
    ('flying', _('Flying'), '#a991ef', ['electric', 'ice', 'rock'], ['grass', 'fight', 'bug']),
    ('ground', _('Ground'), '#d9c35e', ['water', 'grass', 'ice'], ['fire', 'electric', 'poison', 'rock', 'steel']),
    ('poison', _('Poison'), '#984597', ['ground', 'psychic'], ['grass', 'fairy']),
    ('fighting', _('Fighting'), '#c02d26', ['fly', 'psychic', 'fairy'], ['normal', 'ice', 'rock', 'dark', 'steel']),
    ('ice', _('Ice'), '#9ed5d8', ['fire', 'fight', 'rock', 'steel'], ['grass', 'ground', 'flying', 'dragon']),
    ('grass', _('Grass'), '#7ac358', ['fire', 'ice', 'poison', 'flying', 'bug'], ['water', 'ground', 'rock']),
    ('electric', _('Electric'), '#f7cd2d', ['ground'], ['water', 'flying']),
    ('water', _('Water'), '#6b90eb', ['electric', 'grass'], ['fire', 'ground', 'rock']),
    ('fire', _('Fire'), '#ee8031', ['water', 'ground', 'rock'], ['grass', 'ice', 'bug', 'steel']),
    ('normal', _('Normal'), '#a7ab79', ['fight'], []),
]

POKEMON_TYPES_DICT = {
    t[0]: {
        'name': t[1],
        'color': t[2],
        'weak': t[3],
        'strong': t[4],
    } for t in POKEMON_TYPES }

POKEMON_TYPES_DATABASE_CHOICES = [(raw, localized) for (raw, localized, color, weak, strong) in POKEMON_TYPES]
