#!/usr/bin/env python
# -*- coding: utf-8 -*-

from numpy import NaN
from pandas import DataFrame, read_csv, to_numeric
from model import engine, execute_file, execute_query


# table name to store the dataframe
TABLE_NAME_TO_STORE_DF = 'places_pilot_area2'  # correct table
# TABLE_NAME_TO_STORE_DF = 'places_pilot_area_test'  # fake table to test
PATH_CSV_TO_READ_DF = 'TABELAO_2019_12_11.csv'  # original file
# PATH_CSV_TO_READ_DF = 'TABELAO_2019_12_11_sample_last_656_rows.csv'  # this is a sample file


class BigTable():

    __ASTERISKS_NUMBER_TO_PRINT = 100

    def __init__(self, path_csv_to_read_df, table_name_to_store_df):
        self.path_csv_to_read_df = path_csv_to_read_df
        self.table_name_to_store_df = table_name_to_store_df

        # dataframe `Big Table`
        self.df_bt = read_csv('entrada/{}'.format(self.path_csv_to_read_df))
        print('\n`{}` file has been read successfully!'.format(self.path_csv_to_read_df))
        self.__print_asterisks()

        self.__df_bt_pre_processing()

        # create a dataframe to store the rows with some error with the same columns from the original dataframe
        self.df_error = DataFrame(columns=self.df_bt.columns)
        # create a column in order to store the error reason
        self.df_error['reason'] = ''

    def __df_bt_pre_processing(self):
        # rename the columns
        self.df_bt.rename(columns={
            'id_da rua': 'id_street', 'Id_ponto': 'id_point', 'metragem': 'metre', 'logradouro': 'address',
            'numero': 'number', 'numero original': 'original_n', 'Data inicial': 'initial_date', 'Data_final': 'final_date',
            'fonte': 'source', 'autor_da_alimentação': 'author', 'Data': 'date'
        }, inplace=True)

        # add some columns
        self.df_bt['cordinate'] = ''
        self.df_bt['first_day'] = NaN
        self.df_bt['first_month'] = NaN
        self.df_bt['first_year'] = NaN
        self.df_bt['last_day'] = NaN
        self.df_bt['last_month'] = NaN
        self.df_bt['last_year'] = NaN

        # fix some columns
        self.df_bt['metre'] = self.df_bt['metre'].str.replace(',', '.').astype(float)
        self.df_bt['number'] = self.df_bt['number'].str.replace(',', '.').astype(float)

        # print('\noriginal dataframe...')
        # print('\nself.df_bt.head(): \n', self.df_bt.head())
        # print('\nself.df_bt.head(): \n', self.df_bt.head()[['initial_date', 'final_date']])
        print('self.df_bt original length: ', len(self.df_bt))

    def __database_pre_processing(self):
        # create the function in the database
        execute_file('sql/01_saboya_geometry_plsql.sql')
        print('`01_saboya_geometry_plsql.sql` file has been executed successfully!')

        # drop the table if it exists in order to create it again based on the dataframe
        execute_query('DROP TABLE IF EXISTS public.{};'.format(self.table_name_to_store_df))
        print('\nTable `{}` has been dropped successfully!'.format(self.table_name_to_store_df))

    def __check_dates(self, row):
        """
        Processes initial and final dates.

        Return:
            status (boolean):
                True: if processing is OK;
                False: if an error has been found during processing.
        """

        if row.initial_date is not NaN:
            initial_date = row.initial_date.split('/')

            if len(initial_date) != 3:
                self.df_error = self.df_error.append(self.df_bt.loc[[row.Index]])
                self.df_error.at[row.Index, 'reason'] = 'Invalid initial_date.'
                self.df_bt.drop(row.Index, inplace=True)
                return False

            self.df_bt.at[row.Index, 'first_day'] = initial_date[0]
            self.df_bt.at[row.Index, 'first_month'] = initial_date[1]
            self.df_bt.at[row.Index, 'first_year'] = initial_date[2]
        # else:
        #     print('error 1: ', row, '\n')

        if row.final_date is not NaN:
            final_date = row.final_date.split('/')

            if len(final_date) != 3:
                self.df_error = self.df_error.append(self.df_bt.loc[[row.Index]])
                self.df_error.at[row.Index, 'reason'] = 'Invalid final_date.'
                self.df_bt.drop(row.Index, inplace=True)
                return False

            self.df_bt.at[row.Index, 'last_day'] = final_date[0]
            self.df_bt.at[row.Index, 'last_month'] = final_date[1]
            self.df_bt.at[row.Index, 'last_year'] = final_date[2]
        # else:
        #     print('error 2: ', row, '\n')

        return True

    def __process_df_bt(self):
        # create a copied dataframe to iterate over it while I remove the records from the original one
        df_bt_copy = self.df_bt.copy()

        for row in df_bt_copy.itertuples():

            ##################################################
            # validate the dates
            ##################################################

            # one date must have a value, if both are NaN, then add it to the error dataframe
            if row.initial_date is NaN and row.final_date is NaN:
                self.df_error = self.df_error.append(self.df_bt.loc[[row.Index]])
                self.df_error.at[row.Index, 'reason'] = 'Initial and final dates are empty.'
                self.df_bt.drop(row.Index, inplace=True)
                continue

            # if an error has been found during processing, then go to the next row
            if not self.__check_dates(row):
                continue

            # if first_year is greater than last_year, then add it to the error dataframe
            if self.df_bt.at[row.Index, 'first_year'] > self.df_bt.at[row.Index, 'last_year']:
                self.df_error = self.df_error.append(self.df_bt.loc[[row.Index]])
                self.df_error.at[row.Index, 'reason'] = 'Initial year is greater than final year.'
                self.df_bt.drop(row.Index, inplace=True)
                continue

            ##################################################
            # calculate the coordinate
            ##################################################

            # create the SQL query
            query = 'SELECT saboya_geometry({}, {}) AS saboya_geometry;'.format(row.id_street, row.metre)

            # print(row.Index, ' - ', query)

            result = execute_query(query)
            result = result.fetchone()

            self.df_bt.at[row.Index, 'cordinate'] = result['saboya_geometry']

        print('Big table has been processed successfully!')

    def __df_bt_post_processing(self):
        # drop some columns
        self.df_bt.drop(['address', 'metre', 'initial_date', 'final_date', 'id_point'], axis=1, inplace=True)

        print('Big table dataframe - tail(): \n', self.df_bt.tail())
        print('\nBig table dataframe actual length: ', len(self.df_bt))

        print('\n\nBig table error dataframe - tail(): \n', self.df_error.tail())
        print('\nBig table error dataframe length: ', len(self.df_error))

    def __save_dfs_as_csv_files(self):
        # save the dataframes in CSV files
        self.df_bt.to_csv('saida/clean_{}'.format(self.path_csv_to_read_df), index=False)  # original CSV without bad rows
        self.df_error.to_csv('saida/error_{}'.format(self.path_csv_to_read_df), index=False)  # just the bad rows

        print('CSV files (clean and error) have been created successfully!')

    def __save_df_bt_in_the_database(self):
        # save the dataframe in the table `self.table_name_to_store_df` in the database
        self.df_bt.to_sql(self.table_name_to_store_df, con=engine, schema='public')

        print('Big table has been saved in the database successfully!')

    def __database_post_processing(self):
        # execute post processing file
        execute_file('sql/02_post_processing.sql', mapping_template={'table_name': self.table_name_to_store_df})
        print('`02_post_processing.sql` file has been executed successfully!')

    def __print_asterisks(self):
        print()  # simulate a '\n'
        print('*' * self.__ASTERISKS_NUMBER_TO_PRINT, '\n')

    def process_me(self):
        self.__print_asterisks()

        self.__database_pre_processing()
        self.__print_asterisks()

        self.__process_df_bt()
        self.__print_asterisks()

        self.__df_bt_post_processing()
        self.__print_asterisks()

        self.__save_dfs_as_csv_files()
        self.__print_asterisks()

        self.__save_df_bt_in_the_database()
        self.__print_asterisks()

        self.__database_post_processing()
        self.__print_asterisks()

        print('OK!\n')


big_table = BigTable(PATH_CSV_TO_READ_DF, TABLE_NAME_TO_STORE_DF)
big_table.process_me()
