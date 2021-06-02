# big_table_processing

Big Table processing.


## Installation

Install a specific Python version using `pyenv`:

```
$ pyenv install 3.8.5
```

Create a Python environment with the Python version above through `pyenv-virtualenv`:

```
$ pyenv virtualenv 3.8.5 pauliceia_big_table_processing
```

Activate the virtual environment:

```
$ pyenv activate pauliceia_big_table_processing
```

Install the requirements:

```
$ pip install -r requirements.txt
```


### Run the script

Before starting, you need to run a PostgreSQL service with a Pauliceia database.

Activate the virtual environment:

```
$ pyenv activate pauliceia_big_table_processing
```

Run the application:

```
$ python main.py
```
