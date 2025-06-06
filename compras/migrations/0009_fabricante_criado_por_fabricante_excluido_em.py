# Generated by Django 5.2 on 2025-05-01 19:13

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('compras', '0008_fabricante_alter_compra_fabricante_produto'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='fabricante',
            name='criado_por',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='fabricante',
            name='excluido_em',
            field=models.DateTimeField(blank=True, default=None, null=True),
        ),
    ]
