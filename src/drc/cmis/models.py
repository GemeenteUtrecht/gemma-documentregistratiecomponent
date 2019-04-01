from django.core.exceptions import FieldDoesNotExist
from django.db import models

from .choices import ChangeLogStatus
from .utils import get_model_field, get_model_value


class ChangeLog(models.Model):
    token = models.BigIntegerField()
    created_on = models.DateTimeField(auto_now_add=True, unique=True)
    status = models.CharField(max_length=20, choices=ChangeLogStatus.choices, default=ChangeLogStatus.in_progress)

    class Meta:
        verbose_name = 'Changelog'
        verbose_name_plural = 'Changelogs'
        ordering = ('created_on', )


class CMISMixin(models.Model):
    CMIS_MAPPING = {}

    class Meta:
        abstract = True

    def get_cmis_properties(self, allow_none=True):
        """
        Returns the CMIS properties as dict.

        :param allow_none: Converts `None` to  empty string if `False` (default).
        :return: The `dict` of CMIS properties.
        """
        result = {}
        for cmis_property, field_name in self.CMIS_MAPPING.items():
            try:
                field_class = get_model_field(self.__class__, field_name)
            except FieldDoesNotExist:
                field_class = None

            val = get_model_value(self, field_name)
            if val is None:
                if not allow_none:
                    val = ''
            result[cmis_property] = val

        return result

    cmis_properties = property(get_cmis_properties)

    def update_cmis_properties(self, new_cmis_properties, commit=False):
        """
        Only mapped properties are handled. Other properties passed to
        `new_cmis_properties` are ignored.

        :param new_cmis_properties: A `dict` of CMIS properties.
        :param commit: Indicate whether the updated objects should be saved.
        :return: A `set` of updated model instances.
        """
        raise NotImplementedError()
