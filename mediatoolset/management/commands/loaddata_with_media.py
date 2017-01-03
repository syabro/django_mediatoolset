import os

import shutil
from django.conf import settings
from django.core import serializers
from django.core.management.commands.loaddata import Command as LoaddataCommand
from django.db.models import FileField


class Command(LoaddataCommand):
    def handle(self, *fixture_labels, **options):
        super(Command, self).handle(*fixture_labels, **options)
        for fixture_label in fixture_labels:
            for fixture_file, fixture_dir, fixture_name in self.find_fixtures(fixture_label):
                _, ser_fmt, cmp_fmt = self.parse_name(os.path.basename(fixture_file))
                open_method, mode = self.compression_formats[cmp_fmt]
                fixture = open_method(fixture_file, mode)
                objects = serializers.deserialize(ser_fmt, fixture, using=self.using, ignorenonexistent=self.ignore)
                for obj in list(objects):
                    self.process_object_from_fixture(obj.object, fixture_dir)

    def process_object_from_fixture(self, object_from_fixture, fixture_dir):
        fields = [field for field in type(object_from_fixture)._meta.get_fields() if isinstance(field, FileField)]
        for field in fields:
            relative_file_path = getattr(object_from_fixture, field.name).name
            if not relative_file_path:
                continue
            src_path = os.path.join(fixture_dir, 'media', relative_file_path)
            if not os.path.exists(src_path):
                print "Source files %s doesn't exist. Skipping." % src_path
                continue

            target_path = os.path.join(settings.MEDIA_ROOT, relative_file_path)

            if not os.path.exists(os.path.dirname(target_path)):
                os.makedirs(os.path.dirname(target_path))

            if os.path.exists(target_path):
                os.remove(target_path)
            shutil.copy(src_path, target_path)
