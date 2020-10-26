import os
SECRET_KEY = os.urandom(32)
# Grabs the folder where the script runs.
basedir = os.path.abspath(os.path.dirname(__file__))

# Enable debug mode.

# Connect to the database
class config(object):
    DEBUG = True
    SQLALCHEMY_DATABASE_URI = os.environ.get('postgresql://postgres:4795863251O@localhost:5432/postgres')
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # def __init__(self, *args):
    #     super(config, self).__init__(*args))
        

# TODO IMPLEMENT DATABASE URL
SQLALCHEMY_DATABASE_URI = 'postgresql://postgres:4795863251O@localhost:5432/postgres'

