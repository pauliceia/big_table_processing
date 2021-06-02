from os import getenv


# big table processing (BTP) environemnt variables
# table name to store the dataframe in the database
BTP_TABLE_NAME = getenv('BTP_TABLE_NAME', 'places_pilot_area2')
# CSV file that constains the Big Table
BTP_CSV_PATH = getenv('BTP_CSV_PATH', 'TABELAO_2019_12_11.csv')

# PostgreSQL connection
PGUSER = getenv('PGUSER', 'postgres')
PGPASSWORD = getenv('PGPASSWORD', 'postgres')
PGHOST = getenv('PGHOST', 'localhost')
PGPORT = int(getenv('PGPORT', 5432))
PGDATABASE = getenv('PGDATABASE', 'pauliceia')
