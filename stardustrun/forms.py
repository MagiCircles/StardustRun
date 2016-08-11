# -*- coding: utf-8 -*-
import datetime
from django import forms
from django.utils.translation import ugettext_lazy as _, string_concat
from django.db.models.fields import BLANK_CHOICE_DASH
from django.conf import settings as django_settings
from stardustrun import models

############################################################
# Internal tools

class FormWithRequest(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super(FormWithRequest, self).__init__(*args, **kwargs)

class FormSaveOwner(FormWithRequest):
    def save(self, commit=True):
        instance = super(FormSaveOwner, self).save(commit=False)
        instance.owner = self.request.user if self.request.user.is_authenticated() else None
        if commit:
            instance.save()
        return instance

class DateInput(forms.DateInput):
    input_type = 'date'

def date_input(field):
    field.widget = DateInput()
    field.widget.attrs.update({
        'class': 'calendar-widget',
        'data-role': 'data',
    })
    field.help_text = ' '
    return field

############################################################
# Account

class _AccountForm(FormWithRequest):
    starter_id = forms.ChoiceField(choices=BLANK_CHOICE_DASH + django_settings.STARTERS, required=False)

    def __init__(self, *args, **kwargs):
        super(_AccountForm, self).__init__(*args, **kwargs)
        self.fields['team'].required = False
        self.fields['starter_id'].label = _('Starter')
        if self.instance.pk:
            self.fields['starter_id'].initial = self.instance.starter_id

    def save(self, commit=True):
        instance = super(_AccountForm, self).save(commit=False)
        starter_id = self.cleaned_data.get('starter_id', None)
        if starter_id:
            instance.starter_id = int(starter_id)
        else:
            instance.starter_id = None
        if not instance.nickname:
            instance.nickname = self.request.user.username
        if not instance.team:
            instance.team = None
        if instance.team and instance.level < 5:
            instance.team = None
        if commit:
            instance.save()
        return instance

class AccountForm(_AccountForm):
    class Meta:
        model = models.Account
        fields = ('level', 'starter_id', 'team')

class AdvancedAccountForm(_AccountForm):
    def __init__(self, *args, **kwargs):
        super(AdvancedAccountForm, self).__init__(*args, **kwargs)
        self.fields['start_date'] = date_input(self.fields['start_date'])
        self.fields['nickname'].initial = self.request.user.username
        for field in ['start_date', 'bought_coins', 'stardust', 'lucky_eggs', 'incenses', 'lure_modules']:
            self.fields[field].required = False

    def clean_start_date(self):
        if 'start_date' in self.cleaned_data:
            if self.cleaned_data['start_date']:
                if self.cleaned_data['start_date'] < datetime.date(2016, 3, 4):
                    raise forms.ValidationError(_('The game didn\'t even existed at that time.'))
                if self.cleaned_data['start_date'] > datetime.date.today():
                    raise forms.ValidationError(_('This date cannot be in the future.'))
        return self.cleaned_data['start_date']

    class Meta:
        model = models.Account
        fields = ('nickname', 'level', 'starter_id', 'team', 'start_date', 'bought_coins', 'stardust', 'lucky_eggs', 'incenses', 'lure_modules')

class FilterAccounts(FormWithRequest):
    search = forms.CharField(required=False)
    starter_id = forms.ChoiceField(choices=BLANK_CHOICE_DASH + django_settings.STARTERS, required=False, label=_('Starter'))
    ordering = forms.ChoiceField(choices=[
        ('level', _('Level')),
        ('start_date', _('Start Date')),
        ('creation', _('Join Date')),
        ('nickname', _('Alphabetical')),
    ], initial='level', required=False)
    reverse_order = forms.BooleanField(initial=True, required=False)

    def __init__(self, *args, **kwargs):
        super(FilterAccounts, self).__init__(*args, **kwargs)
        self.fields['team'].required = False

    class Meta:
        model = models.Account
        fields = ('search', 'team', 'starter_id', 'ordering', 'reverse_order')

############################################################
# Pokémons

class FilterPokemonsForm(FormWithRequest):
    search = forms.CharField(required=False)
    type = forms.ChoiceField(choices=BLANK_CHOICE_DASH + list(models.POKEMON_TYPES_DATABASE_CHOICES), required=False)
    is_available = forms.NullBooleanField(required=False, initial=None, label=_('Available'))
    owned = forms.NullBooleanField(required=False, initial=None, label=_(u'Pokémons in your collection'))
    seen = forms.NullBooleanField(required=False, initial=None, label=_(u'Pokémons you\'ve seen'))
    ordering = forms.ChoiceField(choices=[
        ('id', _(u'Pokémon number')),
        ('name', _(u'Pokémon name')),
        ('max_cp', _('Max CP')),
        ('hit_points', _('Hit Points')),
        ('attack', _('Attack')),
        ('defense', _('Defense')),
        ('catch_rate', _('Catch Rate')),
        ('flee_rate', _('Flee Rate')),
        ('evolution_candies', _('Candies needed to evolve')),
        ('egg_distance', _('Egg Distance')),
    ], initial='id', required=False)
    reverse_order = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super(FilterPokemonsForm, self).__init__(*args, **kwargs)
        if not self.request.user.is_authenticated():
            self.fields.pop('owned')
            self.fields.pop('seen')

    class Meta:
        model = models.Pokemon
        fields = ('search', 'type', 'is_available', 'owned', 'seen', 'ordering', 'reverse_order')

class PokemonForm(FormSaveOwner):
    types = forms.MultipleChoiceField(
        required=False,
        widget=forms.CheckboxSelectMultiple,
        choices=[],
        label=_('Types'),
    )

    def __init__(self, *args, **kwargs):
        super(PokemonForm, self).__init__(*args, **kwargs)
        self.fields['types'].choices = models.POKEMON_TYPES_DATABASE_CHOICES
        if self.instance:
            self.fields['types'].initial = self.instance.types
        for field in ['hit_points', 'attack', 'defense', 'max_cp','catch_rate', 'flee_rate', 'evolution_of', 'evolution_candies', 'egg_distance', 'attacks']:
            self.fields[field].required = False

    def save(self, commit=True):
        instance = super(PokemonForm, self).save(commit=False)
        if 'types' in self.cleaned_data:
            instance.save_types(self.cleaned_data['types'])
        if commit:
            instance.save()
        return instance

    class Meta:
        model = models.Pokemon
        fields = ('id', 'name', 'image', 'types', 'hit_points', 'attack', 'defense', 'max_cp','catch_rate', 'flee_rate', 'evolution_of', 'evolution_candies', 'egg_distance', 'attacks')

############################################################
# Attacks

class AttackForm(FormSaveOwner):
    class Meta:
        model = models.Attack
        fields = ('name', 'type', 'damage', 'energy_increase', 'duration', 'is_special', 'critical_hit_chance', 'energy_requirement')

class FilterAttacksForm(FormWithRequest):
    search = forms.CharField(required=False)
    is_special = forms.NullBooleanField(required=False, initial=None, label=_('Special'))
    ordering = forms.ChoiceField(choices=[
        ('damage', _('Damage')),
        ('energy_increase', _('Energy Increase')),
        ('critical_hit_chance', _('Critical Hit Chance')),
        ('duration', _('Duration')),
        ('energy_requirement', _('Energy Requirement')),
    ], initial='damage', required=False)
    reverse_order = forms.BooleanField(initial=False, required=False)

    def __init__(self, *args, **kwargs):
        super(FilterAttacksForm, self).__init__(*args, **kwargs)
        self.fields['type'].required = False

    class Meta:
        model = models.Attack
        fields = ('search', 'type', 'is_special', 'ordering', 'reverse_order')

############################################################
# Owned Pokemons

class EditOwnedPokemonForm(FormWithRequest):
    def __init__(self, *args, **kwargs):
        super(EditOwnedPokemonForm, self).__init__(*args, **kwargs)
        available_attacks = models.Attack.objects.filter(pokemons_with_attack=self.instance.pokemon_id)
        self.fields['attack'].choices = BLANK_CHOICE_DASH + [(attack.id, unicode(attack)) for attack in available_attacks if not attack.is_special]
        self.fields['special_attack'].choices = BLANK_CHOICE_DASH + [(attack.id, unicode(attack)) for attack in available_attacks if attack.is_special]
        self.fields['cp'] = forms.DecimalField(required=False, label=_('CP'), initial=self.instance.cp, min_value=0, max_value=self.instance.max_cp)
        for field in self.fields.keys():
            self.fields[field].required = False

    def save(self, commit=True):
        instance = super(EditOwnedPokemonForm, self).save(commit=False)
        if not instance.nickname:
            instance.nickname = None
        instance.update_cache_attacks()
        if commit:
            instance.save()
        return instance

    class Meta:
        model = models.OwnedPokemon
        fields = ('nickname', 'cp', 'hp', 'weight', 'height', 'attack', 'special_attack')

class EvolveOwnedPokemonForm(FormWithRequest):
    evolve_to = forms.ChoiceField(choices=[], required=True)

    def __init__(self, *args, **kwargs):
        super(EvolveOwnedPokemonForm, self).__init__(*args, **kwargs)
        self.fields['evolve_to'].choices = [(id, django_settings.ALL_POKEMONS_DICT[id]['name']) for id in self.instance.pokemon.flatten_next_evolutions_ids]
        self.fields['cp'].label = string_concat(_('CP'), ' ', _('after evolution'))
        self.fields['cp'].required = False
        self.fields['hp'].label = string_concat(_('HP'), ' ', _('after evolution'))
        self.fields['hp'].required = False

    def save(self, commit=True):
        instance = super(EvolveOwnedPokemonForm, self).save(commit=False)
        instance.pokemon = models.Pokemon.objects.get(id=self.cleaned_data['evolve_to'])
        if instance.cp > instance.pokemon.max_cp:
            instance.cp = instance.pokemon.max_cp
        # Update cache max cp and and can evolve
        instance.update_cache_for_pokemon()
        # Update seen / caught for new pokemon
        updated = models.Pokedex.objects.filter(account_id=instance.account_id, pokemon=instance.pokemon).update(seen=True, caught=True)
        if not updated:
            models.Pokedex.objects.create(account_id=instance.account_id, pokemon=instance.pokemon, seen=True, caught=True)
        if commit:
            instance.save()
        return instance

    class Meta:
        model = models.OwnedPokemon
        fields = ('evolve_to', 'cp', 'hp')
