# Generated by Django 3.2.6 on 2021-10-19 06:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0014_auto_20211016_1041'),
    ]

    operations = [
        migrations.CreateModel(
            name='Order',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_by', models.CharField(max_length=200)),
                ('phone', models.CharField(max_length=20)),
                ('address', models.CharField(max_length=50)),
                ('status', models.CharField(choices=[('Received', 'Received'), ('Processing', 'Processing'), ('Completed', 'Completed'), ('Cancelled', 'Cancelled')], max_length=10)),
                ('subtotal', models.PositiveIntegerField(default=0)),
                ('total', models.PositiveIntegerField(default=0)),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('cart', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='main.cart')),
            ],
            options={
                'ordering': ('-id',),
            },
        ),
    ]
