from django.contrib.admin.utils import get_fields_from_path
from django.db.models.constants import LOOKUP_SEP

from .choices import CMISObjectType


def get_cmis_object_id_parts(cmis_object_id):
    """
    Returns the actual object ID, version and path, if present.

    :param object_id: A `CmisId`.
    :return: A `tuple` containing the actual object Id, version and path as strings.
    """
    parts = cmis_object_id.split(';')
    version = None
    if len(parts) == 2:
        version = parts[1]
    parts = parts[0].rsplit('/')
    object_id = parts[-1]
    path = None
    if len(parts) == 2:
        path = parts[0]
    return (object_id, version, path)


def get_cmis_object_id(cmis_object_id):
    """
    Returns the actual object ID.

    :param object_id: A `CmisId`.
    :return: The actual CMIS Id as string.
    """
    return get_cmis_object_id_parts(cmis_object_id)[0]


class FolderConfig:
    __slots__ = ['type', 'name']

    def __init__(self, type_=None, name=None):
        if not type_:
            if not name:
                raise AssertionError('Either type or name is required')
        self.type = type_
        self.name = name

    def __repr__(self):
        return ('<{} type_={!r} name={!r}>').format(self.__class__.__name__, self.type, self.name)


def upload_to(zaak_url):
    """
    Return the fully qualified upload path for the zaak, generic case.

    Each item from the return list is a FolderConfig object with either a
    type, name or both defined. If a name is defined, this name will be used
    for the folder name. The type is required to be able to generate the
    appropriate cmis properties.

    :param zaak_url: :class:`string`.
    :return: list of FolderConfig objects, in order of root -> leaf
    """
    return [
        FolderConfig(name='Zaken', type_=CMISObjectType.zaken),
        FolderConfig(type_=CMISObjectType.zaak_folder)
    ]


def get_model_value(obj, field_name):
    """
    Returns the value belonging to `field_name` on `Model` instance.
    This works for related fields.

    Example::

        >>> get_model_value(Zaak, 'zaaktype__zaaktypeomschrijving')
        'Some description'

    """
    fields = field_name.split(LOOKUP_SEP)
    for field in fields:
        obj = getattr(obj, field)

    return obj


def get_model_field(model, field_name):
    """
    Returns the `Field` instance belonging to `field_name` on a `Model`
    instance or class. This works for related fields.

    Example::

        >>> get_model_field(Zaak, 'zaaktype__zaaktypeomschrijving')
        <django.db.models.fields.CharField: zaaktypeomschrijving>

    """
    return get_fields_from_path(model, field_name)[-1]
