from django.db import models


class DjangoStorage(models.Model):
    enkelvoudiginformatieobject = models.OneToOneField('datamodel.EnkelvoudigInformatieObject', on_delete=models.CASCADE, related_name='djangostorage')
    inhoud = models.FileField(upload_to='uploads/%Y/%m/')
    link = models.URLField(
        max_length=200, blank=True,
        help_text='De URL waarmee de inhoud van het INFORMATIEOBJECT op te '
                  'vragen is.',
    )

    def __str__(self):
        return f"document referentie voor {self.enkelvoudiginformatieobject}"
