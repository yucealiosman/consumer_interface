# -*- coding: utf-8 -*-
from django.core.management.base import BaseCommand
import csv
from main.models import Hotel, Destination


class Command(BaseCommand):

    can_import_settings = True

    def add_arguments(self, parser):
        parser.add_argument('csv_path')
        parser.add_argument('type')

    def handle(self, *args, **options):
        filename = options['csv_path']

        with open(filename, 'rb') as file:
                # firstly, remove all rows in the table.
            if options['type'] == 'hotel':
                model = Hotel
            else:
                model = Destination

            spramreader = csv.reader(file, delimiter=",", quotechar='"')

            for row in spramreader:

                try:
                    data = model(coral_code=row[0], name=row[1])
                    data.save()
                except:
                    self.stderr.write(str(row[0]) +
                                      " already exist\n", ending='')


# def handle(self, *args, **options):

        # with open(options["csv_path"]+
                # '/destinations.csv', 'rb') as destinationfile:
        #     spamreader = csv.reader(destinationfile,
                # delimiter=",", quotechar='')
        #     for row in spamreader:
        #
        #         list = row[0]
        #
        #
        #         p = Destination(name=list[1], coral_code=list[0])
        #         p.save()
        #
        # with open(options["csv_path"]+'/hotels.csv', 'rb') as hotelsfile:
        #     spamreader = csv.reader(hotelsfile, delimiter=' ', quotechar='|')
        #     for row in spamreader:
        #
        #         list = row[0]
        #
        #
        #         p = Hotel(name=list[1], coral_code=list[0])
        #         p.save()
