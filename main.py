from peewee import *

db = SqliteDatabase('briansstuffpw.db')

class User(Model):
    name = CharField()
    birthday = DateField()

    class Meta:
        database = db # This model uses the "people.db" database.
