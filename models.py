from peewee import *
from datetime import datetime

db = SqliteDatabase('db.sqlite3')


class BaseModel(Model):
    class Meta:
        database = db


class UserModel(BaseModel):
    username = CharField(max_length=256, null=True)
    next_msg = DateTimeField(default=datetime.now())
    status = CharField(max_length=256, null=True)


class ValentineModel(BaseModel):
    initiator = ForeignKeyField(UserModel, backref='valentines', null=False)
    receiver = CharField(max_length=256, null=True)
    initiator_pseudo = CharField(max_length=256, null=True)
    receiver_pseudo = CharField(max_length=256, null=True)
    theme = CharField(max_length=256, null=True)
    file = CharField(max_length=256, null=True)
    full_path = TextField(null=True)
