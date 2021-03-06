# Generated by Django 2.0.9 on 2018-12-17 10:37

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('datamodel', '0022_auto_20181213_1332_squashed_0024_auto_20181213_1442'),
    ]

    operations = [
        migrations.AddField(
            model_name='enkelvoudiginformatieobject',
            name='ontvangstdatum',
            field=models.DateField(blank=True, help_text='De datum waarop het INFORMATIEOBJECT ontvangen is. Verplicht te registreren voor INFORMATIEOBJECTen die van buiten de zaakbehandelende organisatie(s) ontvangen zijn.', null=True, verbose_name='ontvangstdatum'),
        ),
    ]
