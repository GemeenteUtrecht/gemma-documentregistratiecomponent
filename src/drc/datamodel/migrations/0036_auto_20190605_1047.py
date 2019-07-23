# Generated by Django 2.2.2 on 2019-06-05 10:47

from django.db import migrations
import privates.fields
import privates.storages


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0035_merge_20190605_1036'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='objectinformatieobject',
            options={'verbose_name': 'Zaakinformatieobject', 'verbose_name_plural': 'Zaakinformatieobjecten'},
        ),
        migrations.AlterField(
            model_name='enkelvoudiginformatieobject',
            name='inhoud',
            field=privates.fields.PrivateMediaFileField(storage=privates.storages.PrivateMediaFileSystemStorage(), upload_to='uploads/%Y/%m/'),
        ),
    ]
