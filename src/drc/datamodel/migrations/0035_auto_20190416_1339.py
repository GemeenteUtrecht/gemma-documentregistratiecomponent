# Generated by Django 2.0.13 on 2019-04-16 13:39

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0034_auto_20190322_1125'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='enkelvoudiginformatieobject',
            options={'verbose_name': 'informatieobject', 'verbose_name_plural': 'informatieobject'},
        ),
        migrations.RemoveField(
            model_name='enkelvoudiginformatieobject',
            name='_object_id',
        ),
    ]
