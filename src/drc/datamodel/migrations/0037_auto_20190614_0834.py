# Generated by Django 2.2.2 on 2019-06-14 08:34

from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0036_auto_20190605_1047'),
    ]

    operations = [
        migrations.CreateModel(
            name='EnkelvoudigInformatieObjectCanonical',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('lock', models.CharField(blank=True, default='', help_text='Hash string, which represents id of the lock', max_length=100)),
            ],
        ),
        migrations.AlterModelOptions(
            name='enkelvoudiginformatieobject',
            options={},
        ),
        migrations.AddField(
            model_name='enkelvoudiginformatieobject',
            name='begin_registratie',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AddField(
            model_name='enkelvoudiginformatieobject',
            name='versie',
            field=models.PositiveIntegerField(default=1),
        ),
        migrations.AlterField(
            model_name='enkelvoudiginformatieobject',
            name='uuid',
            field=models.UUIDField(default=uuid.uuid4, help_text='Unieke resource identifier (UUID4)'),
        ),
        migrations.AlterUniqueTogether(
            name='enkelvoudiginformatieobject',
            unique_together={('uuid', 'versie')},
        ),
        migrations.RemoveField(
            model_name='enkelvoudiginformatieobject',
            name='lock',
        ),
        migrations.AddField(
            model_name='enkelvoudiginformatieobject',
            name='canonical',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='datamodel.EnkelvoudigInformatieObjectCanonical'),
        ),
        migrations.AddField(
            model_name='gebruiksrechten',
            name='canonical',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='datamodel.EnkelvoudigInformatieObjectCanonical'),
        ),
        migrations.AddField(
            model_name='objectinformatieobject',
            name='canonical',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='datamodel.EnkelvoudigInformatieObjectCanonical'),
        ),
    ]
