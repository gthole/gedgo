from django.core.management.base import BaseCommand, CommandError

from gedgo.update import update_from_file
from os import path


class Command(BaseCommand):
    args = '<file_path>'
    help = 'Adds a newgedcom with a given .ged file.'

    def handle(self, *args, **options):

        if not len(args) == 1:
            raise CommandError('add_gedcom takes only one argument - the path to a gedcom file.')

        file_name = args[0]
        if not path.exists(file_name):
            raise CommandError('Gedcom file "%s" not found.' % file_name)
        if (not len(file_name) > 4) or (not file_name[-4:] == '.ged'):
            raise CommandError('File "%s" does not appear to be a .ged file.' % file_name)

        update_from_file(None, file_name)
