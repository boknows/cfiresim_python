# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from datetime import datetime
import csv
import codecs


def populate_market_data(apps, schema_editor):
    DataPoint = apps.get_model('market_data', 'DataPoint')

    # Full path and name to your csv file
    csv_filepathname = "/Users/lboland/Personal/src/cfiresim_python/docs/Workbook3.csv"

    dataReader = csv.reader(open(csv_filepathname, 'rU'), delimiter=str(u','), quotechar=str(u'"'))

    for row in dataReader:
        if row[0]:
            data_point = DataPoint()
            d = row[0]
            if d[-2:] == ".1":
                data_point.data_date = datetime(int(d[:4]), 10, 1)
            else:
                data_point.data_date = datetime.strptime(row[0], '%Y.%m')
            data_point.s_and_p_composite = float(row[1])
            if row[2]:
                data_point.dividend = float(row[2])
            if row[3]:
                data_point.earnings = float(row[3])
            if row[4]:
                data_point.cpi = float(row[4])
            if row[5]:
                data_point.long_interest_rate = float(row[6])
            if row[7] and row[7] != "NA":
                data_point.cape = float(row[7])
            data_point.save()

def undo_populate_market_data(apps, schema_editor):
    pass


class Migration(migrations.Migration):

    dependencies = [
        ('market_data', '0001_initial'),
    ]

    operations = [
        migrations.RunPython(populate_market_data, undo_populate_market_data)
    ]
