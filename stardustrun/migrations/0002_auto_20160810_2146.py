# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import stardustrun.models
import django.db.models.deletion
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('stardustrun', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Attack',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100)),
                ('type', models.CharField(max_length=100, choices=[(b'fairy', 'Fairy'), (b'steel', 'Steel'), (b'dark', 'Dark'), (b'dragon', 'Dragon'), (b'ghost', 'Ghost'), (b'rock', 'Rock'), (b'bug', 'Bug'), (b'psychic', 'Psychic'), (b'flying', 'Flying'), (b'ground', 'Ground'), (b'poison', 'Poison'), (b'fighting', 'Fighting'), (b'ice', 'Ice'), (b'grass', 'Grass'), (b'electric', 'Electric'), (b'water', 'Water'), (b'fire', 'Fire'), (b'normal', 'Normal')])),
                ('damage', models.PositiveIntegerField(null=True, verbose_name='Damage')),
                ('energy_increase', models.PositiveIntegerField(null=True, verbose_name='Energy Increase')),
                ('critical_hit_chance', models.PositiveIntegerField(null=True, verbose_name='Critical Hit Chance')),
                ('duration', models.FloatField(null=True, verbose_name='Duration')),
                ('energy_requirement', models.PositiveIntegerField(null=True, verbose_name='Energy Requirement')),
                ('is_special', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='OwnedPokemon',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('cp', models.PositiveIntegerField(null=True, verbose_name='CP')),
                ('hp', models.PositiveIntegerField(null=True, verbose_name='HP')),
                ('weight', models.FloatField(null=True, verbose_name='Weight')),
                ('height', models.FloatField(null=True, verbose_name='Height')),
                ('nickname', models.CharField(max_length=20, null=True, verbose_name='Nickname')),
                ('_cache_last_update', models.DateTimeField(null=True)),
                ('_cache_account_nickname', models.CharField(max_length=20, null=True)),
                ('_cache_account_owner_id', models.PositiveIntegerField(null=True)),
                ('_cache_account_owner_username', models.CharField(max_length=32, null=True)),
                ('_cache_attack_name', models.CharField(max_length=100, null=True)),
                ('_cache_special_attack_name', models.CharField(max_length=100, null=True)),
                ('_cache_can_evolve', models.NullBooleanField(default=None)),
                ('_cache_max_cp', models.PositiveIntegerField(null=True)),
                ('account', models.ForeignKey(related_name='pokemons', to='stardustrun.Account')),
                ('attack', models.ForeignKey(related_name='owned_pokemon_attack', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Attack', to='stardustrun.Attack', null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pokedex',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('candies', models.PositiveIntegerField(default=0, verbose_name='Candies')),
                ('seen', models.BooleanField(default=False, verbose_name='Seen')),
                ('caught', models.BooleanField(default=False, verbose_name='Caught')),
                ('_cache_evolution_chain', models.TextField(null=True, blank=True)),
                ('account', models.ForeignKey(related_name='pokedex', to='stardustrun.Account')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Pokemon',
            fields=[
                ('id', models.PositiveIntegerField(unique=True, serialize=False, verbose_name='Pok\xe9mon number', primary_key=True)),
                ('name', models.CharField(unique=True, max_length=100, verbose_name='Pok\xe9mon name')),
                ('image', models.ImageField(upload_to=stardustrun.models.pokemonUploadTo, verbose_name='Image')),
                ('is_available', models.BooleanField(default=True, verbose_name='Available')),
                ('types_string', models.TextField(null=True, verbose_name='Types', blank=True)),
                ('hit_points', models.PositiveIntegerField(null=True, verbose_name='Hit Points')),
                ('attack', models.PositiveIntegerField(null=True, verbose_name='Attack')),
                ('defense', models.PositiveIntegerField(null=True, verbose_name='Defense')),
                ('max_cp', models.PositiveIntegerField(null=True, verbose_name='Max CP')),
                ('catch_rate', models.PositiveIntegerField(null=True, verbose_name='Catch Rate')),
                ('flee_rate', models.PositiveIntegerField(null=True, verbose_name='Flee Rate')),
                ('evolution_candies', models.PositiveIntegerField(null=True, verbose_name='Candies needed to evolve', choices=[(12, 12), (25, 25), (50, 50), (100, 100), (400, 400)])),
                ('egg_distance', models.PositiveIntegerField(null=True, verbose_name='Egg Distance', choices=[(2, b'2km'), (5, b'5km'), (10, b'10km')])),
                ('_cache_previous_evolutions', models.TextField(null=True, blank=True)),
                ('_cache_next_evolutions', models.TextField(null=True, blank=True)),
                ('attacks', models.ManyToManyField(related_name='pokemons_with_attack', to='stardustrun.Attack')),
                ('evolution_of', models.ForeignKey(related_name='evolutions', on_delete=django.db.models.deletion.SET_NULL, to='stardustrun.Pokemon', null=True)),
                ('owner', models.ForeignKey(related_name='created_pokemons', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='pokedex',
            name='pokemon',
            field=models.ForeignKey(related_name='pokedexes', to='stardustrun.Pokemon'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='pokedex',
            unique_together=set([('account', 'pokemon')]),
        ),
        migrations.AddField(
            model_name='ownedpokemon',
            name='pokemon',
            field=models.ForeignKey(related_name='have_it', to='stardustrun.Pokemon'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ownedpokemon',
            name='special_attack',
            field=models.ForeignKey(related_name='owned_pokemon_special_attack', on_delete=django.db.models.deletion.SET_NULL, verbose_name='Special Attack', to='stardustrun.Attack', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='_cache_last_update',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='_cache_leaderboard',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='_cache_leaderboard_team',
            field=models.PositiveIntegerField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='_cache_leaderboards_last_update',
            field=models.DateTimeField(null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='_cache_owner_email',
            field=models.EmailField(max_length=75, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='_cache_owner_preferences_status',
            field=models.CharField(max_length=12, null=True, choices=[(b'THANKS', b''), (b'SUPPORTER', 'Pok\xe9mon Trainer'), (b'LOVER', 'Super Pok\xe9mon Trainer'), (b'AMBASSADOR', 'Expert Pok\xe9mon Trainer'), (b'PRODUCER', 'Pok\xe9mon Master'), (b'DEVOTEE', 'Ultimate Pok\xe9mon Master')]),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='_cache_owner_preferences_twitter',
            field=models.CharField(max_length=32, null=True, blank=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='_cache_owner_username',
            field=models.CharField(max_length=32, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='bought_coins',
            field=models.PositiveIntegerField(null=True, verbose_name='Bought Pok\xe9coins'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='incenses',
            field=models.PositiveIntegerField(null=True, verbose_name='Incenses'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='lucky_eggs',
            field=models.PositiveIntegerField(null=True, verbose_name='Lucky Eggs'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='lure_modules',
            field=models.PositiveIntegerField(null=True, verbose_name='Lure Modules'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='nickname',
            field=models.CharField(default='', max_length=20, verbose_name='Nickname'),
            preserve_default=False,
        ),
        migrations.AddField(
            model_name='account',
            name='stardust',
            field=models.PositiveIntegerField(null=True, verbose_name='Stardust'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='start_date',
            field=models.DateField(help_text='When you started playing with this account.', null=True, verbose_name='Start Date'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='starter',
            field=models.ForeignKey(related_name='accouts_started_with', on_delete=django.db.models.deletion.SET_NULL, to='stardustrun.Pokemon', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='account',
            name='team',
            field=models.CharField(max_length=10, null=True, verbose_name='Team', choices=[(b'instinct', 'Instinct'), (b'mystic', 'Mystic'), (b'valor', 'Valor')]),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='account',
            name='level',
            field=models.PositiveIntegerField(null=True, verbose_name='Level', db_index=True),
            preserve_default=True,
        ),
    ]
