# Generated by Django 2.0.13 on 2019-04-30 10:57

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('datamodel', '0035_auto_20190416_1339'),
    ]

    operations = [
        migrations.CreateModel(
            name='DjangoStorage',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('inhoud', models.FileField(upload_to='uploads/%Y/%m/')),
                ('link', models.URLField(blank=True, help_text='De URL waarmee de inhoud van het INFORMATIEOBJECT op te vragen is.')),
                ('enkelvoudiginformatieobject', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='djangostorage', to='datamodel.EnkelvoudigInformatieObject')),
            ],
        ),
    ]
