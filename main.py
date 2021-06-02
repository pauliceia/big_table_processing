#!/usr/bin/env python3

from big_table_processing.environment import BTP_CSV_PATH, BTP_TABLE_NAME
from big_table_processing.service import BigTable


big_table = BigTable(BTP_CSV_PATH, BTP_TABLE_NAME)
big_table.process_me()
