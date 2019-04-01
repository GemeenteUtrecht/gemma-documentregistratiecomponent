import logging

from django.core.management.base import BaseCommand
from django.utils.translation import ugettext as _

from ..client import default_client

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    """
    Synchronizes changes in the DMS with our database by calling getContentChanges.
    """
    help = _('Synchroniseert de zaakdocumenten door wijzigingen op te vragen in het DMS.')

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run', '--dryrun',
            action='store_true',
            dest='dryrun',
            default=False,
            help='Retrieves all content changes from the DMS but doesn\'t update the DRC.',
        )

    def handle(self, *args, **options):
        dryrun = options.get('dryrun', False)

        result = default_client.sync(dryrun)

        msg = ', '.join(['{}: {}'.format(k, v) for k, v in result.items()])

        out = self.stdout
        if 'failed' in result and result['failed']:
            out = self.stderr
        out.write('Sync result: {}{}'.format(msg, ' (dryrun)' if dryrun else ''))
