# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stardustrun', '0002_auto_20160810_2146'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ownedpokemon',
            name='_cache_max_cp',
            field=models.PositiveIntegerField(null=True, db_index=True),
            preserve_default=True,
        ),
    ]
