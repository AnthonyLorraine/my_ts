# Generated by Django 4.0.2 on 2022-03-22 04:48

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0009_employee_tutorial_done'),
    ]

    operations = [
        migrations.AddField(
            model_name='penalty',
            name='valid_for_day_count',
            field=models.IntegerField(default=14),
        ),
        migrations.CreateModel(
            name='PenaltyClaim',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('claimed_seconds', models.IntegerField()),
                ('claim_date', models.DateField(auto_now_add=True)),
                ('employee', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to=settings.AUTH_USER_MODEL)),
                ('penalty', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='main.penalty')),
            ],
        ),
    ]
