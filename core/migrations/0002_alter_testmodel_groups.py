# Generated by Django 4.1.3 on 2022-12-05 06:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='testmodel',
            name='groups',
            field=models.ManyToManyField(to='core.testgroupmodel', verbose_name='Принадлежность к группам'),
        ),
    ]