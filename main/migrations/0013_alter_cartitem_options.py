# Generated by Django 3.2.6 on 2021-10-16 07:40

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_cartitem'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='cartitem',
            options={'ordering': ('-id',), 'verbose_name': 'Cart Item', 'verbose_name_plural': 'Cart Items'},
        ),
    ]
