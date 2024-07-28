from peewee import *

db = SqliteDatabase('coins.db')


class BaseModel(Model):
    class Meta:
        database = db


class Сurrency(BaseModel):
    user = CharField(null=True)
    name = CharField(null=True)
    min = FloatField(null=True)
    max = FloatField(null=True)
