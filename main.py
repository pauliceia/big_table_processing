#!/usr/bin/env python
# -*- coding: utf-8 -*-

from big_table_processing.service import BigTable


# table name to store the dataframe
TABLE_NAME_TO_STORE_DF = 'places_pilot_area2'  # correct table
# TABLE_NAME_TO_STORE_DF = 'places_pilot_area_test'  # fake table to test
PATH_CSV_TO_READ_DF = 'TABELAO_2019_12_11.csv'  # original file
# PATH_CSV_TO_READ_DF = 'TABELAO_2019_12_11_sample_last_656_rows.csv'  # this is a sample file


big_table = BigTable(PATH_CSV_TO_READ_DF, TABLE_NAME_TO_STORE_DF)
big_table.process_me()
