from os import getenv

# PostgreSQL connection
PGUSER = getenv('PGUSER', 'postgres')
PGPASSWORD = getenv('PGPASSWORD', 'postgres')
PGHOST = getenv('PGHOST', 'localhost')
PGPORT = int(getenv('PGPORT', 5432))
PGDATABASE = getenv('PGDATABASE', 'pauliceia')
