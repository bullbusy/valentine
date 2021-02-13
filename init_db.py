from models import *
from os import listdir, remove

if 'db.sqlite3' in listdir():
    remove('db.sqlite3')

db.create_tables([UserModel, ValentineModel])
