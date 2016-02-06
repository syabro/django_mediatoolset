import os

from django.conf import settings
from django.core.management import BaseCommand
from django.db import models
from django.db.models import FileField
from progress.bar import Bar


class Command(BaseCommand):
    def handle(self, *fixture_labels, **options):
        media_files = self.get_media_files()

        stale_files = self.get_stale_files(media_files)

        if len(stale_files) == 0:
            print "Yay! 0 stale files found"
            return

        print "%d/%d files are not in db" % (len(stale_files), len(media_files))

        confirm_remove = raw_input("Do you want to remove files that are not db Y/N [N]: ")
        if not confirm_remove.lower() == 'y':
            print "Canceled"
            return

        self.remove_stale_files(stale_files)

    def get_stale_files(self, media_files):
        django_models_with_file_fields = self.get_django_models_with_file_fields()
        stale_files = []
        bar = Bar('Analyzing media files', max=len(media_files))
        for media_file in media_files:
            if not self.remove_file_if_not_exists_in_db(media_file, django_models_with_file_fields):
                stale_files.append(media_file)
            bar.next()
        bar.finish()
        return stale_files

    def remove_stale_files(self, stale_files):
        bar = Bar('Removing media files', max=len(stale_files))
        for stale_file in stale_files:
            os.remove(stale_file)
            bar.next()
        bar.finish()

    def get_media_files(self):
        matches = []
        for root, dirnames, filenames in os.walk(settings.MEDIA_ROOT):
            matches += map(lambda filename: os.path.join(root, filename), filenames)
        return matches

    def get_django_models_with_file_fields(self):
        django_models_with_file_fields = []
        for model in models.get_models(include_auto_created=True):
            fieldnames = [field.name for field in model._meta.get_fields() if isinstance(field, FileField)]
            if fieldnames:
                django_models_with_file_fields.append([model, fieldnames])
        return django_models_with_file_fields

    def remove_file_if_not_exists_in_db(self, filename, models):
        for model, fieldnames in models:
            if filename.startswith(settings.MEDIA_ROOT):
                filename = filename[len(settings.MEDIA_ROOT.rstrip('/') + '/'):]

            kwargs = dict([[fieldname, filename] for fieldname in fieldnames])

            if model.objects.filter(**kwargs).exists():
                return True

        return False




